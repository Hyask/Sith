from django.test import SimpleTestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from core.models import User
from core.views.forms import RegisteringForm, LoginForm

class UserRegistrationTest(SimpleTestCase):
    def setUp(self):
        try:
            Group.objects.create(name="root")
        except:
            pass

    def test_register_user_form_ok(self):
        """
        Should register a user correctly
        """
        c = Client()
        response = c.post(reverse('core:register'), {'first_name': 'Guy',
                                                     'last_name': 'Carlier',
                                                     'email': 'guy@git.an',
                                                     'date_of_birth': '12/6/1942',
                                                     'password1': 'plop',
                                                     'password2': 'plop',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_OK' in str(response.content))

    def test_register_user_form_fail_password(self):
        """
        Should not register a user correctly
        """
        c = Client()
        response = c.post(reverse('core:register'), {'first_name': 'Guy',
                                                     'last_name': 'Carlier',
                                                     'email': 'bibou@git.an',
                                                     'date_of_birth': '12/6/1942',
                                                     'password1': 'plop',
                                                     'password2': 'plop2',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_FAIL' in str(response.content))

    def test_register_user_form_fail_email(self):
        """
        Should not register a user correctly
        """
        c = Client()
        response = c.post(reverse('core:register'), {'first_name': 'Guy',
                                                     'last_name': 'Carlier',
                                                     'email': 'bibou.git.an',
                                                     'date_of_birth': '12/6/1942',
                                                     'password1': 'plop',
                                                     'password2': 'plop',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_FAIL' in str(response.content))

    def test_register_user_form_fail_missing_name(self):
        """
        Should not register a user correctly
        """
        c = Client()
        response = c.post(reverse('core:register'), {'first_name': 'Guy',
                                                     'last_name': '',
                                                     'email': 'bibou@git.an',
                                                     'date_of_birth': '12/6/1942',
                                                     'password1': 'plop',
                                                     'password2': 'plop',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_FAIL' in str(response.content))

    def test_register_user_form_fail_missing_date_of_birth(self):
        """
        Should not register a user correctly
        """
        c = Client()
        response = c.post(reverse('core:register'), {'first_name': '',
                                                     'last_name': 'Carlier',
                                                     'email': 'bibou@git.an',
                                                     'date_of_birth': '',
                                                     'password1': 'plop',
                                                     'password2': 'plop',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_FAIL' in str(response.content))

    def test_register_user_form_fail_missing_first_name(self):
        """
        Should not register a user correctly
        """
        c = Client()
        response = c.post(reverse('core:register'), {'first_name': '',
                                                     'last_name': 'Carlier',
                                                     'email': 'bibou@git.an',
                                                     'date_of_birth': '12/6/1942',
                                                     'password1': 'plop',
                                                     'password2': 'plop',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_FAIL' in str(response.content))

    def test_register_user_form_fail_already_exists(self):
        """
        Should not register a user correctly
        """
        c = Client()
        c.post(reverse('core:register'), {'first_name': 'Guy',
                                          'last_name': 'Carlier',
                                          'email': 'bibou@git.an',
                                          'date_of_birth': '12/6/1942',
                                          'password1': 'plop',
                                          'password2': 'plop',
                                         })
        response = c.post(reverse('core:register'), {'first_name': 'Bibou',
                                                     'last_name': 'Carlier',
                                                     'email': 'bibou@git.an',
                                                     'date_of_birth': '12/6/1942',
                                                     'password1': 'plop',
                                                     'password2': 'plop',
                                                    })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('TEST_REGISTER_USER_FORM_FAIL' in str(response.content))

    def test_login_success(self):
        """
        Should login a user correctly
        """
        c = Client()
        c.post(reverse('core:register'), {'first_name': 'Guy',
                                          'last_name': 'Carlier',
                                          'email': 'bibou@git.an',
                                          'date_of_birth': '12/6/1942',
                                          'password1': 'plop',
                                          'password2': 'plop',
                                         })
        response = c.post(reverse('core:login'), {'username': 'gcarlier', 'password': 'plop'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue('LOGIN_OK' in str(response.content))

    def test_login_fail(self):
        """
        Should not login a user correctly
        """
        c = Client()
        c.post(reverse('core:register'), {'first_name': 'Guy',
                                          'last_name': 'Carlier',
                                          'email': 'bibou@git.an',
                                          'date_of_birth': '12/6/1942',
                                          'password1': 'plop',
                                          'password2': 'plop',
                                         })
        response = c.post(reverse('core:login'), {'username': 'gcarlier', 'password': 'guy'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue('LOGIN_FAIL' in str(response.content))

    def test_create_page_ok(self):
        """
        Should create a page correctly
        """
        c = Client()
        response = c.post(reverse('core:page_prop', kwargs={'page_name': 'guy'}), {'parent': '',
                                                                                   'name': 'guy',
                                                                                   'title': 'Guy',
                                                                                   'Content': 'Guyéuyuyé',
                                                                                  })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('PAGE_SAVED' in str(response.content))

    def test_create_child_page_ok(self):
        """
        Should create a page correctly
        """
        c = Client()
        c.post(reverse('core:page_prop', kwargs={'page_name': 'guy'}), {'parent': '',
                                                                        'name': 'guy',
                                                                        'title': 'Guy',
                                                                        'Content': 'Guyéuyuyé',
                                                                       })
        response = c.post(reverse('core:page_prop', kwargs={'page_name': 'guy/bibou'}), {'parent': '1',
                                                                                         'name': 'bibou',
                                                                                         'title': 'Bibou',
                                                                                         'Content':
                                                                                         'Bibibibiblblblblblbouuuuuuuuu',
                                                                                        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue('PAGE_SAVED' in str(response.content))

    def test_access_child_page_ok(self):
        """
        Should display a page correctly
        """
        c = Client()
        c.post(reverse('core:page_prop', kwargs={'page_name': 'guy'}), {'parent': '',
                                                                        'name': 'guy',
                                                                        'title': 'Guy',
                                                                        'Content': 'Guyéuyuyé',
                                                                       })
        c.post(reverse('core:page_prop', kwargs={'page_name': 'guy/bibou'}), {'parent': '1',
                                                                              'name': 'bibou',
                                                                              'title': 'Bibou',
                                                                              'Content':
                                                                              'Bibibibiblblblblblbouuuuuuuuu',
                                                                             })
        response = c.get(reverse('core:page', kwargs={'page_name': 'guy/bibou'}))
        self.assertTrue(response.status_code == 200)
        self.assertTrue('PAGE_FOUND : Bibou' in str(response.content))

    def test_access_page_not_found(self):
        """
        Should not display a page correctly
        """
        c = Client()
        response = c.get(reverse('core:page', kwargs={'page_name': 'swagg'}))
        self.assertTrue(response.status_code == 200)
        self.assertTrue('PAGE_NOT_FOUND' in str(response.content))

#TODO: many tests on the pages:
#   - renaming a page
#   - changing a page's parent --> check that page's children's full_name
#   - changing the different groups of the page