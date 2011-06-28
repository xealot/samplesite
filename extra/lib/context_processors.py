def step_processor(request):
    return {'step': getattr(request, 'step_num', 0)}