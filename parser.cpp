#include <string.h>
#include <errno.h>

#include <jsbit.h>
#include <jsscript.h>
#include <jsapi.h>
#include <jsparse.h>
#include <jsscan.h>
#include <jsfun.h>
#include <jscntxt.h>
#include <jsstr.h>
#include <json.h>

static jsval
JS_ValueToJSON(JSContext *cx, jsval value)
{
    JSObject *json = js_NewObject(cx, &js_JSONClass, NULL, NULL, 0);

    jsval func = JSVAL_VOID;
    JS_AddRoot(cx, &func);

    JS_GetMethod(cx, json, "stringify", NULL, &func);

    jsval args[] = {value};
    jsval ret = JSVAL_VOID;
    JS_AddRoot(cx, &ret);
    JS_AddRoot(cx, &value);
    JS_AddRoot(cx, &args);

    if (!JS_CallFunctionValue(cx, json, func, 1, args, &ret)) {
        ret = JSVAL_VOID;
        JS_GetPendingException(cx, &ret);
        JS_ClearPendingException(cx);
    }

    //JS_RemoveRoot(cx, &args);
    //JS_RemoveRoot(cx, &func);

    return ret;
}

static JSObject *
createAndAddToParentObject(JSContext *cx, JSObject *parent, const char *name)
{
     JSObject *obj = JS_NewObject(cx, NULL, NULL, NULL);
     jsval v = OBJECT_TO_JSVAL(obj);
     JS_AddRoot(cx, &v);
     JS_SetProperty(cx, parent, name, &v);
     return obj;
}

static void
prettify(JSContext *cx, JSObject *parent, JSParseNode *pn)
{
    JSObject *obj;
    jsval v;
    JSBool ok;

    if (!obj) {
        perror("failed to construct obj");
    }
    ok = (v = INT_TO_JSVAL(pn->pn_type),
          JS_SetProperty(cx, parent, "type", &v)) &&
         (v = INT_TO_JSVAL(pn->pn_op),
          JS_SetProperty(cx, parent, "op", &v)) &&
         (v = INT_TO_JSVAL(pn->pn_arity),
          JS_SetProperty(cx, parent, "arity", &v)) &&
         (v = INT_TO_JSVAL(pn->pn_pos.begin.index),
          JS_SetProperty(cx, parent, "index", &v)) &&
         (v = INT_TO_JSVAL(pn->pn_pos.begin.lineno),
          JS_SetProperty(cx, parent, "lineno", &v));
    if (!ok) {
        perror("failed to set obj props");
    }

    if (pn->pn_atom && ATOM_IS_STRING(pn->pn_atom)) {
        v = ATOM_KEY(pn->pn_atom);
        JS_SetProperty(cx, parent, "atom", &v);
    }

    switch (pn->pn_arity) {
        case PN_LIST: {
            JSObject *array = JS_NewArrayObject(cx, 0, NULL);
            v = OBJECT_TO_JSVAL(array);
            JS_SetProperty(cx, parent, "list", &v);

            int i = 0;
            for (JSParseNode *n = pn->pn_head; n; n = n->pn_next) {
                obj = JS_NewObject(cx, NULL, NULL, NULL);
                v = OBJECT_TO_JSVAL(obj);
                JS_AddRoot(cx, &v);
                JS_SetElement(cx, array, i++, &v);
                prettify(cx, obj, n);
                JS_RemoveRoot(cx, &v);
            }
            break;
        }
        case PN_NAME:
            if (pn->expr()) {
                obj = createAndAddToParentObject(cx, parent, "expr");
                prettify(cx, obj, pn->expr());
            }
            break;
        case PN_NAMESET:
            if (pn->pn_tree) {
                obj = createAndAddToParentObject(cx, parent, "tree");
                prettify(cx, obj, pn->pn_tree);
            }
            break;
        case PN_UNARY:
            if (pn->pn_kid) {
                obj = createAndAddToParentObject(cx, parent, "kid");
                prettify(cx, obj, pn->pn_kid);
            }
            break;
        case PN_BINARY:
            if (pn->pn_left) {
                obj = createAndAddToParentObject(cx, parent, "left");
                prettify(cx, obj, pn->pn_left);
            }
            if (pn->pn_right) {
                obj = createAndAddToParentObject(cx, parent, "right");
                prettify(cx, obj, pn->pn_right);
            }
            break;
        case PN_TERNARY:
            if (pn->pn_kid1) {
                obj = createAndAddToParentObject(cx, parent, "kid1");
                prettify(cx, obj, pn->pn_kid1);
            }
            if (pn->pn_kid2) {
                obj = createAndAddToParentObject(cx, parent, "kid2");
                prettify(cx, obj, pn->pn_kid2);
            }
            if (pn->pn_kid3) {
                obj = createAndAddToParentObject(cx, parent, "kid3");
                prettify(cx, obj, pn->pn_kid3);
            }
            break;
        case PN_FUNC: {
            if (pn->pn_body) {
                obj = createAndAddToParentObject(cx, parent, "body");
                prettify(cx, obj, pn->pn_body);

            }
            JSObjectBox * objbox = static_cast<JSObjectBox*>(pn->pn_funbox);
            JSFunction * fun = GET_FUNCTION_PRIVATE(cx, objbox->object);
            v = ATOM_KEY(fun->atom);
            JS_SetProperty(cx, parent, "name", &v);
            break;
        }
        case PN_NULLARY:
            break;
        default:
            printf("%d unhandled\n", pn->pn_arity);
            break;
    }

    switch (pn->pn_type) {
        case TOK_NUMBER:
            //double d;
            //JS_ValueToNumber(cx, pn->pn_dval, &d);
            //printf(", \"dval\": %g", 1138.0);
            break;
        default:
            break;
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "need a filename\n");
        return 1;
    }
    char * filename = argv[1];

    FILE * file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "could not open file: %s: %s\n", filename, strerror(errno));
        return 1;
    }

    JSRuntime * runtime = JS_NewRuntime(8L * 1024L * 1024L);
    if (runtime == NULL) {
        fprintf(stderr, "cannot create runtime\n");
        return 1;
    }

    JSContext * cx = JS_NewContext(runtime, 8192);
    if (cx == NULL) {
        fprintf(stderr, "cannot create context\n");
        return 1;
    }
    JS_SetOptions(cx,
                  JS_GetOptions(cx) |
                  JSOPTION_DONT_REPORT_UNCAUGHT |
                  JSOPTION_STRICT);

    // w/ let statement please.
    JS_SetVersion(cx, (JSVersion)180);
    JS_SetGCParameterForThread(cx, JSGC_MAX_CODE_CACHE_BYTES, 512 * 1024 * 1024);

    JSObject * global = JS_NewObject(cx, NULL, NULL, NULL);
    JS_InitStandardClasses(cx, global);

    JSExceptionState * exnState = JS_SaveExceptionState(cx);
    JSCompiler jsc(cx);
    if (jsc.init(NULL, 0, file, filename, 1)) {
        JSErrorReporter older = JS_SetErrorReporter(cx, NULL);
        JSParseNode *node = jsc.parse(NULL);
        if (!node) {
            fprintf(stderr, "could not compile: %s: %d at line %d\n",
                    filename, jsc.tokenStream.flags, jsc.tokenStream.lineno);
            return 1;
        }
        JSObject *obj = JS_NewObject(cx, NULL, NULL, NULL);
        prettify(cx, obj, node);
        jsval objval = OBJECT_TO_JSVAL(obj);
        JS_AddRoot(cx, &objval);
        jsval json = JS_ValueToJSON(cx, objval);

        JSString *string = JS_ValueToString(cx, json);
        if (!string) perror("boo");
        printf("%s\n", JS_GetStringBytes(string));

        JS_RemoveRoot(cx, &json);
        JS_RemoveRoot(cx, &objval);

        JS_SetErrorReporter(cx, older);
    }
    JS_RestoreExceptionState(cx, exnState);

    return 0;
}
