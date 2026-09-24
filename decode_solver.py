class Solver:
    def __init__(self, normalized_df):
        columns = ['name', 'frameType', 'attribute', 'type', 'levelRankLink', 'atk', 'def']
        self.pool = normalized_df[columns].copy()        
        self.pool['levelRankLink'] = self.pool['levelRankLink'].fillna(0).astype(int)
        self.next()

    def next(self):
        if self.pool.empty:
            print("pool empty")
            return

        if len(self.pool) <= 3:
            print(f"candidates ({len(self.pool)} left): {self.pool['name'].tolist()}")
            return

        # mode of properties to find the most common traits in the current pool
        core_traits = ['frameType', 'attribute', 'levelRankLink', 'type']
        trait_counts = self.pool.groupby(core_traits, as_index=False).size()
        best_traits = trait_counts.sort_values(by='size', ascending=False).iloc[0]
        
        # filter to match
        sub_pool = self.pool[
            (self.pool['frameType'] == best_traits['frameType']) &
            (self.pool['attribute'] == best_traits['attribute']) &
            (self.pool['levelRankLink'] == best_traits['levelRankLink']) &
            (self.pool['type'] == best_traits['type'])
        ]
        
        optimal_atk = sub_pool['atk'].mode()[0]
        optimal_def = sub_pool['def'].mode()[0]
        
        exact_matches = sub_pool[(sub_pool['atk'] == optimal_atk) & (sub_pool['def'] == optimal_def)]
        rec_card = exact_matches['name'].iloc[0] if not exact_matches.empty else sub_pool['name'].iloc[0]
        
        print(f"\n{len(self.pool)} cards remaining.")
        print(f"Next guess: '{rec_card}' ({best_traits['frameType']} / {best_traits['attribute']} / LvRkLk {best_traits['levelRankLink']} / {best_traits['type']} / {int(optimal_atk)} ATK / {int(optimal_def)} DEF)")

    def guess(self, property_name, value, is_match):
        self.pool = self.pool[self.pool[property_name] == value] if is_match else self.pool[self.pool[property_name] != value]
        self.next()

    def hint(self, property_name, correct_value):
        self.pool = self.pool[self.pool[property_name] == correct_value]
        self.next()
