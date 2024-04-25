SELECT 
  ?ms                                              # Mineral Site URI
  ?ms_name                                         # Mineral Site Name
  ?deposit_name                                    # Deposit Type Name
  ?country                                         # Country
  ?loc_wkt                                         # WKT Geometry
  ?total_tonnage_measured
  ?total_tonnage_indicated
  ?total_tonnage_inferred
  ?total_contained_measured
  ?total_contained_indicated
  ?total_contained_inferred
  (?total_tonnage_measured + ?total_tonnage_indicated + ?total_tonnage_inferred AS ?total_tonnage)                     # Total Tonnage [million tonnes]
  (?total_contained_measured + ?total_contained_indicated + ?total_contained_inferred AS ?total_contained_metal)
  (IF(?total_tonnage > 0, ?total_contained_metal / ?total_tonnage, 0) AS ?total_grade)                                 # Total Grade
WHERE {
  {
    SELECT ?ms ?ms_name ?deposit_name ?country ?loc_wkt
           (SUM(?tonnage_measured) AS ?total_tonnage_measured)
           (SUM(?tonnage_indicated) AS ?total_tonnage_indicated)
           (SUM(?tonnage_inferred) AS ?total_tonnage_inferred)
           (SUM(?contained_measured) AS ?total_contained_measured)
           (SUM(?contained_indicated) AS ?total_contained_indicated)
           (SUM(?contained_inferred) AS ?total_contained_inferred)
    WHERE {
        {
           SELECT ?ms (MAX(?confidence) AS ?max_confidence)
           WHERE {
              ?ms :deposit_type_candidate/:confidence ?confidence .
           }
           GROUP BY ?ms
        }
    
        ?ms :deposit_type_candidate ?deposit_candidate_with_max_conf .
        ?deposit_candidate_with_max_conf :confidence ?deposit_confidence .
        ?deposit_candidate_with_max_conf :normalized_uri [ rdfs:label ?deposit_name ] .
        FILTER(?deposit_confidence = ?max_confidence)
    
        ?ms :mineral_inventory ?mi .
        OPTIONAL { ?ms rdfs:label|:name ?ms_name . }
        OPTIONAL {
            ?ms :location_info [ :country ?country; :location ?loc_wkt ] .
            FILTER(datatype(?loc_wkt) = geo:wktLiteral)
        }
        
        ?mi :category ?mi_cat .
        ?mi :commodity [ :name "$commodity" ] .
    
        {
            SELECT ?mi (MAX(?ore_val) AS ?max_ore_val) (SAMPLE(?grade_val) AS ?matched_grade_val)
            WHERE {
                ?mi :ore [ :ore_value ?ore_val_raw; :ore_unit ?ore_unit] .
                OPTIONAL { ?mi :grade [ :grade_value ?grade_val; :grade_unit ?grade_unit] . }
                BIND(IF(bound(?ore_val_raw), ?ore_val_raw, 0) AS ?ore_val_pre)
                BIND(IF(?ore_unit = <https://minmod.isi.edu/resource/Q202>, ?ore_val_pre, IF(?ore_unit = <https://minmod.isi.edu/resource/Q200>, ?ore_val_pre / 1e6, ?ore_val_pre)) AS ?ore_val)
            }
            GROUP BY ?mi
        }
    
        BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "measured"), ?max_ore_val, 0) AS ?tonnage_measured)
        BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "indicated"), ?max_ore_val, 0) AS ?tonnage_indicated)
        BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "inferred"), ?max_ore_val, 0) AS ?tonnage_inferred)
    
        BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "measured") && ?matched_grade_val > 0, ?max_ore_val * ?matched_grade_val, 0) AS ?contained_measured)
        BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "indicated") && ?matched_grade_val > 0, ?max_ore_val * ?matched_grade_val, 0) AS ?contained_indicated)
        BIND(IF(CONTAINS(LCASE(STR(?mi_cat)), "inferred") && ?matched_grade_val > 0, ?max_ore_val * ?matched_grade_val, 0) AS ?contained_inferred)
    
    }
    GROUP BY ?ms ?ms_name ?deposit_name ?country ?loc_wkt
  }
}