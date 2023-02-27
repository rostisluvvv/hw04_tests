from django.test import TestCase


class CoreURLTests(TestCase):

    def test_core_404_render_custom_templates(self):
        templates_url_names: dict = {
            '/unexisting_page/': 'core/404.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
