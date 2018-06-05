from django.shortcuts import redirect

class ExemplaryPlannerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        print(self.get_object().user.id)
        user = self.request.user
        if user:
            if user.id == self.get_object().user.id:
                self.template_name = 'city_guide/planner.html'
                return super(ExemplaryPlannerMixin, self).dispatch(request, *args, **kwargs)
            elif self.get_object().user.id == 1:
                self.template_name = 'city_guide/planner_examplary.html'
                return super(ExemplaryPlannerMixin, self).dispatch(request, *args, **kwargs)
            else:
                redirect('city_guide:index')
        return redirect('city_guide:index')