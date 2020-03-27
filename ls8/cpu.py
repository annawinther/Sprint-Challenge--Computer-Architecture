"""CPU functionality."""

import sys
 
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # reg is 8 
        self.reg = [0] * 8
        # ram is 256
        self.ram = [0] * 256
        # add pc to 0
        self.pc = 0
        # initialise the branchtable to empty dictionary
        self.branchtable = {}
        # set the branchtable operations function
        self.branch_operations()
        # add a stack pointer (SP) and set to empty at adress 0xF4
        self.stack_pointer = 0xF4


    def load(self, program):
        """Load a program into memory."""

        address = 0
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    ### Branch Operations ###
    def LDI(self, reg_a, data):
        self.reg[reg_a] = data
        self.pc += 3

    def PRN(self, a, b):
        print(self.reg[a])
        self.pc += 2

    ### AUL Operations ###
    # Add the value in two registers and store the result in registerA.
    def ADD(self, a, b):
        self.alu("ADD", a, b)
        self.pc += 3
        
    # MUL is the resposibility of the ALU 
    # Here it calls the alu() function passing in operant_a and operand_b to get the work done
    def MUL(self, a, b):
        self.alu("MUL", a, b)
        self.pc += 3
    
    ### Stack Operations ###
    # Push the value in the given register on the stack.
    def PUSH(self, a, b):
        # Decrement the `SP`
        self.stack_pointer -= 1
        # Copy the value in the given register to the address pointed to by sp
        val = self.reg[a]
        # Insert value onto stack
        self.ram_write(val, self.stack_pointer)
        self.pc += 2
    
    # Pop the value at the top of the stack into the given register
    def POP(self, a, b):
        # Copy the value from the address pointed to by `SP` to the given register.
        stack_value = self.ram[self.stack_pointer]
        self.reg[a] = stack_value
        # We cannot move past the top of the stack, so once we reach 0xFF, we shouldn't increase the pointer
        if self.stack_pointer != 0xFF:
            # Increment `SP`
            self.stack_pointer += 1
        self.pc += 2

    # Calls a subroutine (function) at the address stored in the register. (01010000)
    def CALL(self, a, b):
        # The address of the ***instruction*** _directly after_ `CALL` is
        # pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        # The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location
        self.stack_pointer -= 1
        # store return address (self.pc + 2) in stack (return address is the next instruction address)
        return_adr = self.pc + 2
        self.ram_write(return_adr, self.stack_pointer)
        # then move the pc to the subroutine address
        self.pc = self.reg[a]
    
    # Return from subroutine. (00010001)
    def RET(self, a, b):
        # Pop the value from the top of the stack and store it in self.pc.
        stack_value = self.ram[self.stack_pointer]
        # so the next cycle will go from there
        self.pc = stack_value


    def branch_operations(self):
        self.branchtable[0b10000010] = self.LDI
        self.branchtable[0b01000111] = self.PRN
        self.branchtable[0b10100010] = self.MUL
        self.branchtable[0b10100000] = self.ADD
        self.branchtable[0b01000110] = self.POP
        self.branchtable[0b01000101] = self.PUSH
        self.branchtable[0b01010000] = self.CALL
        self.branchtable[0b00010001] = self.RET

    def ram_read(self, adress):
        return self.ram[adress]

    def ram_write(self, value, address):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # add MUL operation
        # Multiply the values in two registers together and store the result in registerA.
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")
       

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # set running to be True
        running = True
        while running:
        # needs to read mem address stores in register PC and store in IR - local variable
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # if IR = `HLT` (1)
            if IR == 0b00000001:
                # Halt the CPU (and exit the emulator).
                print("Halting operations")
                running = False
                break
            # else if IR is not in the branchtable 
            elif IR not in self.branchtable:
                # print an Invalid Instruction message amd set running to False to exit
                print(f"Invalid Instruction {IR}")
                running = False
            # otherwise
            else:
                # use the branchtable to run the correct operation
                self.branchtable[IR](operand_a, operand_b)
