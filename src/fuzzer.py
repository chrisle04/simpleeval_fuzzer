# Fuzzer for simpleeval Expressions
# This file generates a mix of random mathematical expressions that are both valid and invalid,
# and tests them by sending them to the targets.py file for evaluation through stdin.

import subprocess
import random
import string
import simpleeval
import glob
import os

def load_seed_corpus(dir='corpus'):
    """Load all seed files from the corpus directory"""
    seeds = []
    if os.path.exists(dir):
        txt_files = glob.glob(os.path.join(dir, '*.txt'))  
        for file_path in txt_files:  
            try:
                with open(file_path, 'r') as f:
                    seed_content = f.read().strip()
                    if seed_content: 
                        seeds.append(seed_content) 
            except Exception as e:
                print(f" Could not load seed file {file_path}: {e}")
        
        print(f"Loaded {len(seeds)} seeds from {dir}/")
    else:
        print(f"Corpus directory {dir}/ not found")
    
    return seeds

def delete_random_character(s):
    """Delete a random character from the string"""
    if len(s) == 0:
        return s
    index = random.randint(0, len(s) - 1)
    return s[:index] + s[index + 1:]

def insert_random_character(s):
    """Insert a random character at a random position in the string"""
    operators = ['+', '-', '/', '*', '%', '**', '==', '!=', '<', '>', '<=', '>=', '^', '|', '&', '<<', '>>']
    if len(s) == 0:
        return s + random.choice(string.ascii_letters + string.digits + ''.join(operators))
    index = random.randint(0, len(s))
    char = random.choice(string.ascii_letters + string.digits + ''.join(operators))
    return s[:index] + char + s[index:]

def flip_random_character(s):
    """Flip a random character in the string to a different character"""
    if len(s) == 0:
        return s
    index = random.randint(0, len(s) - 1)
    char = random.choice(string.ascii_letters + string.digits + '+-*/%**==!=<><=^|&<<>>')
    return s[:index] + char + s[index + 1:]

def mutate_operators(seed):
    """Mutate mathematical operators in the expression"""
    operators = ['+', '-', '*', '/', '%', '**', '==', '!=', '<', '>', '<=', '>=', '&', '|', '^', '<<', '>>']
    for op in operators:
        if op in seed:
            new_op = random.choice([o for o in operators if o != op])
            return seed.replace(op, new_op, 1) 
    return seed

def mutate_structure(seed):
    """Mutate structure of the expression"""
    mutations = [
        lambda s: f"({s})",           
        lambda s: f"{s} + 1",         
        lambda s: f"abs({s})",        
        lambda s: s.replace('(', '').replace(')', ''), 
    ]
    mutation = random.choice(mutations)
    return mutation(seed)

def mutate_expression(expr):
    """Mutate the expression by randomly deleting, inserting, flipping characters or changing 
    structure or operators"""
    mutation_type = random.choice(['delete', 'insert', 'flip', 'structure', 'operator'])
    
    if mutation_type == 'delete':
        return delete_random_character(expr)
    elif mutation_type == 'insert':
        return insert_random_character(expr)
    elif mutation_type == 'flip':
        return flip_random_character(expr)
    elif mutation_type == 'structure':
        return mutate_structure(expr)
    elif mutation_type == 'operator':
        return mutate_operators(expr)
    else:
        return expr  # Holder, should not reach line


def generate_input(seed_corpus):
    """Generate mix of valid and invalid inputs"""
    # if random.random() < 0.7:  # 70% valid expressions
    #     return generate_math_input() 
    # else:  # 30% invalid expressions
    #     return generate_invalid_input()
    
    # Hybrid strategy with seeds
    strategy_weights = {
        'seed_exact': 15,        # 25% - Use seed 
        'seed_mutated': 45,      # 35% - Mutate seed with techniques   
        'generated_valid': 25,   # 25% - Generate new valid
        'generated_invalid': 15  # 15% - Generate new invalid
    }
    
    strategy = random.choices(
        list(strategy_weights.keys()),
        weights=list(strategy_weights.values())
    )[0]
    
    if strategy == 'seed_exact':
        return random.choice(seed_corpus)
    elif strategy == 'seed_mutated':
        base_seed = random.choice(seed_corpus)
        return mutate_expression(base_seed)
    elif strategy == 'generated_valid':
        return generate_math_input()
    else: 
        return generate_invalid_input()
    
def random_value():
    """Generate Random number from 1 to 1000, float from 1 to 10, 
    random negative number from -1000 to 1, random float from -10 to 1
    or variable name"""
    numbers = [str(random.randint(1, 1000)), 
               str(random.uniform(1, 10)), 
               str(random.randint(-1000, 1)), 
               str(random.uniform(-10, 1))]
    variables = ['x', 'y', 'z', 'pi', 'e', 'value']
    return random.choice(numbers + variables)

def generate_math_input():
    """Generate valid mathematical expressions"""
    # Operators for fuzzing
    binary_operators = ['+', '-', '/', '*', '%', '**', '==', '!=', '<', '>', '<=', '>=']
    bitwise_operators = ['^', '|', '&', '<<', '>>']
    
    functions = ['abs', 'max', 'min', 'round'] 
    
    type = random.choice(['binary', 'number', 'variable', 'function', 'if'])
    
    if type == 'binary':
        left = random_value()
        right = random_value()
        
        all_operators = binary_operators + bitwise_operators
        operation = random.choice(all_operators)
        
        if operation == '/' and right == '0':
            right = str(random.randint(1, 100))
        
        return f"{left} {operation} {right}"
    elif type == 'variable':
        variables = ['x', 'y', 'z', 'pi', 'e', 'value']
        left = random.choice(variables)
        if random.random() < 0.2: 
            return left # 20% just return variable
        else:
            # operation with variable
            right = random_value()
            all_operators = binary_operators + bitwise_operators
            operation = random.choice(all_operators)
        
            if operation == '/' and right == '0':
                right = str(random.randint(1, 100))
        
        return f"{left} {operation} {right}"
    elif type == 'function':
        func = random.choice(functions)
        
        if func in ['max', 'min']:
            a = random_value()
            b = random_value()
            return f"{func}({a}, {b})"
        else:
            a = random_value()
            return f"{func}({a})"
    elif type == 'if':
        cond1 = ''.join(random.choices(string.ascii_uppercase, k=1))
        cond2 = ''.join(random.choices(string.ascii_uppercase, k=1))
        cond3 = ''.join(random.choices(string.ascii_uppercase, k=1))
        val1 = str(random.randint(1, 10))
        val2 = str(random.randint(1, 10))
        val3 = str(random.randint(1, 10))

        return f"'{cond1}' if {val1} > {val2} else '{cond2}' if {val3} < {val2} else '{cond3}'" 
    else:
        return random_value()

def generate_invalid_input():
    """Generate unusual and invalid expressions to test error handling"""
    undef_func = ['maximum', 'minimum', 'rounding', 'multiply', 'add', 'abs_value', 'log10', 'sqrt', 'exp', 'sin', ''.join(random.choices(string.ascii_uppercase, k=5))]
    invalid_expressions = [
        lambda: ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=random.randint(3, 20))),
        lambda: random.choice(['', ' ', '()', '((()))', 'undefined_var', '1++2', '**2', '1///2', '1+2*', 'c']),
        lambda: str(random.randint(1, 100)) + random.choice(['(', ')', '[', ']', '{', '}']) * random.randint(1, 5),
        lambda: random.choice(['import os',
                               'exec("print(\'Hello World\')")',
                               '__import__("os")', 'eval("0+1")',
                               'objdump -d src/fuzzer.py',
                               'dir()',
                               'locals()',
                               'globals()',
        ]),
        lambda: random.choice(undef_func)
    ]

    exp = random.choice(invalid_expressions)()
    if exp in undef_func:
        if exp in ['maximum', 'minimum', 'multiply', 'add']:
            a = random_value()
            b = random_value()
            return f"{exp}({a}, {b})"
        else:
            a = random_value()
            return f"{exp}({a})"
    else:
        return exp
    

success = 0
errors = 0
timeouts = 0
crashes = 0
seed_corpus = load_seed_corpus('corpus')

# Run the fuzzing loop
for i in range(1000):
    """Run main fuzzer loop for 1000 iterations"""
    # Get fuzzer input
    fuzz_input = generate_input(seed_corpus)
    print(f"Case {i+1}/1000 with input: {fuzz_input}")
    # execute input into target script
    try:
        proc = subprocess.Popen(
            ['python3', 'src/targets.py'], 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = proc.communicate(input=fuzz_input, timeout=5)
        
        if proc.returncode == 0:
            print(f"Input: {fuzz_input}, Result: {stdout.strip()}")
            success += 1
        else:
            print(f"Input: {fuzz_input}, Error: {stderr.strip()}")
            errors += 1
            
    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"Input: {fuzz_input}, Error: Timeout")
        timeouts += 1
    except Exception as e:
        print(f"Input: {fuzz_input}, Error: {e}")
        crashes += 1

print(f"\nFuzzer Testing Summary\n------------------------")
print(f"Success: {success}\nErrors: {errors}\nTimeouts: {timeouts}\nCrashes: {crashes}")