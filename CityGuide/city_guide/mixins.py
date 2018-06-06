from django.shortcuts import redirect, reverse

class ExemplaryPlannerMixin(object):
    def dispatch(self, request, *args, **kwargs):
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

class NotUserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user and user.is_authenticated:
            return redirect(reverse(self.redirect_url))
        else:
            return super(NotUserMixin, self).dispatch(request, *args, **kwargs)
