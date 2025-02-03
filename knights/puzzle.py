from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


# Puzzle 0
# A says "I am both a knight and a knave."
propo0 = And(AKnight, AKnave)
knowledge0 = And(
    # TODO
    Or(AKnight, AKnave),
    Implication(AKnight, propo0),
    Implication(AKnave, Not(propo0))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
propo1 = And(AKnave, BKnave)
knowledge1 = And(
    # TODO
    Or(AKnight, AKnave),
    Or(BKnave, BKnight),
    # A says "We are both knaves."
    Implication(AKnight, propo1),
    Implication(AKnave, Not(propo1))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
propo2a = Or(And(AKnight, BKnight), And(AKnave, BKnave))
propo2b = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
    # TODO
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    # A says "We are the same kind."
    Implication(AKnight, propo2a),
    Implication(AKnave, Not(propo2a)),
    # B says "We are of different kinds."
    Implication(BKnight, propo2b),
    Implication(BKnave, Not(propo2b)),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO
    # default
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    # A says either "I am a knight." or "I am a knave.", but you don't know which.
    Implication(AKnight, Or(AKnight, AKnave)),
    Implication(AKnave, (Not(Or(AKnave, AKnight)))),
    # B says "A said 'I am a knave'."
    Implication(BKnight, Or(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))),
    Implication(BKnave, Or(Implication(AKnight, Not(AKnave)), Implication(AKnave, Not(Not(AKnave))))),
    # B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),
    # C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
