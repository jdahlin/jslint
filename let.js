let x = 0.6;
let a = 1, b = 2, c = 3;

let f = function func() {
    let y = z + x + 1;
    let test = 1;
    let f = function nested() {
        let e = a + b + c + d + test;
    }();
}();
