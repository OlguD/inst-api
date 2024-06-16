from get_cookie import is_two_factor_required, login_v2


two_factor_bool, response_json = is_two_factor_required('x',
                                                        'x')

print(two_factor_bool, response_json)
