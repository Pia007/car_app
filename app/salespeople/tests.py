from django.urls import reverse

#Unit Test
def test_salespeople_list_access():
    url = reverse('salespeople_list')
    assert url == "/salespeople/"

def test_salespeople_detail_access():
    url = reverse('salespeople_detail', args=[1])
    assert url == "/salespeople/1/"

def test_salespeople_new_access():
    url = reverse('salespeople_new')
    assert url == "/salespeople/new/"



