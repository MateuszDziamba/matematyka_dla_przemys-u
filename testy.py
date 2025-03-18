import math

def cosine_between_vectors(v1, v2):
    # Rozpakowanie współrzędnych
    a, b = v1
    x, y = v2
    
    # Obliczenie iloczynu skalarnego
    dot_product = a * x + b * y
    
    # Obliczenie długości wektorów
    magnitude_v1 = math.sqrt(a ** 2 + b ** 2)
    magnitude_v2 = math.sqrt(x ** 2 + y ** 2)
    
    # Zabezpieczenie przed dzieleniem przez zero
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        raise ValueError("Jeden z wektorów ma zerową długość.")
    
    # Obliczenie cosinusa kąta
    cosine = dot_product / (magnitude_v1 * magnitude_v2)
    
    return cosine

v1 = [3, 4]
v2 = [4, -3]
print(cosine_between_vectors(v1, v2))  # Wynik: 0.0 (czyli kąty proste)

v1 = [0, 4]
v2 = [4, -3]
print(cosine_between_vectors(v1, v2))  # Wynik: 0.0 (czyli kąty proste)

v1 = [3, 40]
v2 = [0, 25]
print(cosine_between_vectors(v1, v2))  # Wynik: 0.0 (czyli kąty proste)

v1 = [1, 101]
v2 = [0, 1]
print(cosine_between_vectors(v1, v2))  # Wynik: 0.0 (czyli kąty proste)


print(bool(0))