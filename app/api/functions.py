def aq_get_names_from_locations_list(locations):
    names = []
    for item in locations:
        names.append(item[3])
    return names


def at_get_names_from_locations_list(locations):
    names = []
    for item in locations:
        names.append(item[5])
    return names
