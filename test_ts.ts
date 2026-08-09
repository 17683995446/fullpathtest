
export class TestClass {
    public name: string;
    private value: number;
    
    constructor(name: string) {
        this.name = name;
        this.value = 0;
    }
    
    public increment(): void {
        this.value++;
    }
    
    public getValue(): number {
        return this.value;
    }
}
