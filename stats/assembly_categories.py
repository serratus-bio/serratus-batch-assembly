def get_category(total_length, nb_contigs):
        category = 'D'
        if   total_length > 25000  and nb_contigs == 1:
            category = 'A'
        elif total_length > 25000  and nb_contigs > 1:
            category = 'B'
        elif total_length > 5000 and total_length <= 25000:
            category = 'C'
        elif nb_contigs == 0:
            category = 'E'
        return category
