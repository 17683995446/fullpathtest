
class TestClass {
    constructor(name) {
        this.name = name;
        this.value = 0;
    }
    
    increment() {
        this.value++;
    }
    
    getValue() {
        return this.value;
    }
}

module.exports = TestClass;
