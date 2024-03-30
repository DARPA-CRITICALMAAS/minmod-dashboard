SELECT ?ms ?name ?msr ?mss ?loc_wkt
      WHERE {
          ?ms a :MineralSite .
          ?ms :name ?name .
          ?ms :record_id ?msr .
          ?ms :source_id ?mss .
          ?ms :location_info [ :location ?loc_wkt ] .
          
          ?ms :mineral_inventory ?mi .
          ?mi :commodity [ :name "$commodity"@en ] .
      }
