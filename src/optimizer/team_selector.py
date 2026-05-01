# src/optimizer/team_selector.py

import pulp
from src.utils.helpers import generate_mock_surfers

def optimize_team(df, power_surfer_man=None, power_surfer_woman=None):
    """
    Selecciona el equipo óptimo de 12 surfistas (6 hombres + 6 mujeres)
    con exactamente 2 por cada tier (A,B,C) en cada género.
    Opcionalmente, duplica la puntuación de los Power Surfers.
    """
    # Copia para no modificar el original
    data = df.copy()
    
    # Aplicar Power Surfers (duplicar puntuación)
    if power_surfer_man:
        if power_surfer_man in data["surfer"].values:
            idx = data[data["surfer"] == power_surfer_man].index[0]
            data.loc[idx, "total_score"] *= 2
        else:
            print(f"Advertencia: {power_surfer_man} no está en los datos. Ignorado.")
    
    if power_surfer_woman:
        if power_surfer_woman in data["surfer"].values:
            idx = data[data["surfer"] == power_surfer_woman].index[0]
            data.loc[idx, "total_score"] *= 2
        else:
            print(f"Advertencia: {power_surfer_woman} no está en los datos. Ignorado.")
    
    # Crear problema de maximización
    prob = pulp.LpProblem("Fantasy_WSL_Optimizer", pulp.LpMaximize)
    
    # Variables binarias para cada surfista
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in data.index}
    
    # Función objetivo: maximizar suma de total_score * x_i
    prob += pulp.lpSum(data.loc[i, "total_score"] * x[i] for i in data.index)
    
    # Restricción: exactamente 6 hombres
    prob += pulp.lpSum(x[i] for i in data[data.gender == "M"].index) == 6
    # Restricción: exactamente 6 mujeres
    prob += pulp.lpSum(x[i] for i in data[data.gender == "F"].index) == 6
    
    # Restricciones: por cada género y cada tier, exactamente 2 surfistas
    for gender in ["M", "F"]:
        for tier in ["A", "B", "C"]:
            indices = data[(data.gender == gender) & (data.tier == tier)].index
            if len(indices) > 0:
                prob += pulp.lpSum(x[i] for i in indices) == 2
            else:
                print(f"Advertencia: no hay surfistas género {gender} tier {tier}")
    
    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    # Extraer los seleccionados (donde x_i == 1)
    seleccionados = data.loc[[i for i in data.index if x[i].value() == 1]]
    return seleccionados

def main():
    # Generar datos mock
    df = generate_mock_surfers()
    
    # Definir Power Surfers de ejemplo (cambia según prefieras)
    power_man = "John John Florence"
    power_woman = "Carissa Moore"
    
    # Optimizar
    equipo = optimize_team(df, power_man, power_woman)
    
    # Mostrar resultados
    print("=== EQUIPO RECOMENDADO (basado en techo histórico) ===\n")
    for genero in ["M", "F"]:
        nombre_genero = "Hombres" if genero == "M" else "Mujeres"
        print(f"\n--- {nombre_genero}")
        for tier in ["A", "B", "C"]:
            subset = equipo[(equipo.gender == genero) & (equipo.tier == tier)]
            if not subset.empty:
                nombres = ", ".join(subset["surfer"].values)
                print(f"  Tier {tier}: {nombres}")
    
    print("\n=== POWER SURFERS ===")
    print(f"Hombre: {power_man if power_man in df['surfer'].values else 'Ninguno'}")
    print(f"Mujer: {power_woman if power_woman in df['surfer'].values else 'Ninguno'}")
    
    print(f"\nPuntuación total esperada: {equipo['total_score'].sum():.2f} puntos")
    print("(Nota: esta puntuación ya incluye el doble de los Power Surfers)")

if __name__ == "__main__":
    main()