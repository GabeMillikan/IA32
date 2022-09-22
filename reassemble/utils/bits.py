def extract(data: int, *groups: int) -> tuple[int]:
    '''
    Extract groups of bits from an integer.

    >>> extract(0b11101010, 2, 3, 3) == (0b11, 0b101, 0b010)
    True

    >>> extract(0b00111000_11101010, 6, 4, 4, 2) == (0b001110, 0b0011, 0b1010, 0b10)
    True
    '''

    results: list[int] = []
    for group in reversed(groups):
        results.append(data & ((1 << group) - 1))
        data >>= group

    return tuple(reversed(results))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
