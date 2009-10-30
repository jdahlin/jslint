function Foo(args) {
    this._init(args);
}

Foo.prototype = {
    _init : function(args) {
        this._foo = 'foo' in args ? args.foo : null;
    },

    get bar() {
        return this._bar;
    },

    get foo() {
        return this._foo;
    }
};
