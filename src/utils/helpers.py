# src/utils/helpers.py

import pandas as pd
import numpy as np

def generate_mock_surfers(seed=42):
    """
    Genera un DataFrame con surfistas ficticios.
    Ahora garantiza que haya al menos 2 surfistas de cada género por cada tier (A,B,C)
    para que las restricciones del optimizador sean factibles.
    """
    np.random.seed(seed)
    
    hombres = [
        "John John Florence", "Gabriel Medina", "Jack Robinson",
        "Ethan Ewing", "Italo Ferreira", "Filipe Toledo",
        "Griffin Colapinto", "Kanoa Igarashi", "Connor O'Leary",
        "Leonardo Fioravanti", "Imaikalani deVault", "Barron Mamiya"
    ]
    mujeres = [
        "Carissa Moore", "Tyler Wright", "Tatiana Weston-Webb",
        "Brisa Hennessy", "Molly Picklum", "Bettylou Sakura Johnson",
        "Stephanie Gilmore", "Johanne Defay", "Lakey Peterson",
        "Caroline Marks", "Isabelle Nichols", "Sally Fitzgibbons"
    ]
    
    round_scores = {
        "Winner": 100,
        "Finalist": 60,
        "Semifinalist": 35,
        "Quarterfinalist": 20,
        "Round16": 10,
        "Round32": 5,
        "Round64": 2
    }
    rondas = list(round_scores.keys())
    probs = [0.05, 0.10, 0.15, 0.20, 0.25, 0.20, 0.05]
    
    datos = []
    
    # Para garantizar al menos 2 por tier, podemos asignar manualmente los primeros 6 surfistas
    # y luego el resto al azar. O simplemente repetir hasta que se cumpla.
    # Haremos una función auxiliar:
    def asignar_tiers_con_garantia(nombres, genero):
        # Queremos que cada tier tenga al menos 2 surfistas
        # Como hay 12 nombres, podemos asignar 2 a cada tier (total 6) y el resto aleatorio
        tiers_asignados = []
        # Primero, forzamos 2 por tier
        for tier in ["A", "B", "C"]:
            tiers_asignados.extend([tier] * 2)
        # Luego, los 6 restantes (porque 12 - 6 = 6) se asignan aleatoriamente
        restantes = np.random.choice(["A","B","C"], size=6, p=[0.25,0.5,0.25])
        tiers_asignados.extend(restantes)
        # Mezclar para que no queden todos los fijos al principio
        np.random.shuffle(tiers_asignados)
        return tiers_asignados
    
    tiers_h = asignar_tiers_con_garantia(hombres, "M")
    tiers_m = asignar_tiers_con_garantia(mujeres, "F")
    
    for i, nombre in enumerate(hombres):
        tier = tiers_h[i]
        best_round = np.random.choice(rondas, p=probs)
        last_round = np.random.choice(rondas, p=probs)
        familiarity = np.random.uniform(0.3, 1.0)
        datos.append([nombre, "M", tier, best_round, last_round, familiarity])
    
    for i, nombre in enumerate(mujeres):
        tier = tiers_m[i]
        best_round = np.random.choice(rondas, p=probs)
        last_round = np.random.choice(rondas, p=probs)
        familiarity = np.random.uniform(0.3, 1.0)
        datos.append([nombre, "F", tier, best_round, last_round, familiarity])
    
    df = pd.DataFrame(datos, columns=[
        "surfer", "gender", "tier", 
        "best_round", "last_round", 
        "wave_familiarity"
    ])
    
    df["best_round_score"] = df["best_round"].map(round_scores)
    df["last_round_score"] = df["last_round"].map(round_scores)
    
    df["total_score"] = (0.7 * df["best_round_score"] + 
                         0.2 * df["last_round_score"] + 
                         0.1 * df["wave_familiarity"] * 100)
    
    return df

if __name__ == "__main__":
    df = generate_mock_surfers()
    print("Verificación de conteo mínimo (debe haber al menos 2 por género/tier):")
    print(df.groupby(["gender", "tier"]).size())