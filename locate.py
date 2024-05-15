from maps.disca_map import rss_map, RSS_NULL

def least_squares_classification(rss_map, available_gateways, new_data):
    new_data_gateways = list(new_data.keys())
    categories = list(rss_map.keys())
    scores = {}
    
    #Completar rss_map con gateways faltantes
    for category in rss_map.keys():
        category_gateways = rss_map[category].keys()
        for gateway in available_gateways:
            if gateway not in category_gateways:
                rss_map[category][gateway] = {}
                for ch in range(8):
                    rss_map[category][gateway][ch] = RSS_NULL
                
    # Completar new_data con valores RSS nulos
    for missing_gateway in available_gateways:
        if missing_gateway not in new_data_gateways:
            new_data[missing_gateway]={}
            existing_channels = list(new_data[new_data_gateways[0]].keys())
            for existing_channel in existing_channels:
                new_data[missing_gateway][existing_channel] = RSS_NULL
        
    
    gateways = list(new_data.keys())
    
    for category in categories:
        squared_errors = []
        for gateway in gateways:
            gateway_rss = rss_map[category][gateway]
            new_data_rss = new_data[gateway]
            for channel in new_data_rss.keys():
                if channel in gateway_rss:
                    squared_error = (new_data_rss[channel] - gateway_rss[channel])**2
                    squared_errors.append(squared_error)
        
        # Suma de errores cuadráticos
        total_squared_error = sum(squared_errors)
        scores[category] = total_squared_error
    
    # Encontrar la categoría con el menor error cuadrático
    best_category = min(scores, key=scores.get)
    return best_category, scores

def main():
    available_gateways = ["rak7248-grc-pm65","main-gtw-grc","itaca-upv-022"]
    new_data = { #0e
        "main-gtw-grc": {0: -96.66666666666667, 1: -95.0, 2: -96.25, 3: -99.0, 4: -98.25, 5: -97.0, 6: -98.4, 7: -97.66666666666667}
    }
    classification, error_scores = least_squares_classification(rss_map, available_gateways, new_data)
    print(f"El nuevo dato pertenece a la categoría: '{classification}' con los siguientes puntajes de error: {error_scores}")

if __name__ == "__main__":
    main()
