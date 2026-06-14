from django.views.generic import DetailView, ListView
from applications.enrollment.models import Enrollment, Program



class EnrollmentList(ListView):
    template_name = "enrollment/children_list.html"
    context_object_name = "enrollment"
    paginate_by = 25
    queryset = Enrollment.objects.all()
    
class EnrollmentDetailView(DetailView):
    template_name = "enrollment/enrollment_detail.html"
    context_object_name = "enrollment"
    queryset = Enrollment.objects.select_related("child")