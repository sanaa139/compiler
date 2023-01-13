def get(num: int):
    return f"GET {num}"

def set(num: int):
    return f"SET {num}"

def put(num: int):
    return f"PUT {num}"

def load(num: int):
    return f"LOAD {num}"

def sub(num: int):
    return f"SUB {num}"

def add(num: int):
    return f"ADD {num}"

def jzero():
    return f"JZERO "

def jpos():
    return f"JPOS "

def jump():
    return f"JUMP "

def store(num: int):
    return f"STORE {num}"