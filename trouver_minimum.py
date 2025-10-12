def trouver_minimum(liste):
    if not liste:
        return None
    minimum = liste[0]
    for element in liste:
        if element < minimum:
            minimum = element
    return minimum
