def check_valid_id(item_id: int):
    print('inside the check', item_id % 5, item_id)
    if item_id % 5 == 0:
        raise ValueError('Id can\'t be multiple of 5')
    return item_id