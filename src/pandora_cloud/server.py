# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from os import getenv
from os.path import join, abspath, dirname

from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response
from pandora.exts.token import check_access_token
from pandora.openai.auth import Auth0
from werkzeug.middleware.proxy_fix import ProxyFix

__version__ = '0.3.2'


class ChatBot:
    build_id = 'MYarkpkg17PeZHlffaxc-'

    def __init__(self, proxy=None, debug=False, sentry=False):
        self.proxy = proxy
        self.debug = debug
        self.sentry = sentry
        self.login_local = getenv('LOGIN_LOCAL', True)
        self.log_level = logging.DEBUG if debug else logging.WARN
        self.api_prefix = getenv('CHATGPT_API_PREFIX',
                                 'https://ai.fakeopen.com')

    @staticmethod
    def after_request(resp):
        resp.headers['X-Server'] = 'pandora-cloud/{}'.format(__version__)

        return resp

    @staticmethod
    def __set_cookie(resp, token, expires):
        resp.set_cookie('access-token', token, expires=expires,
                        path='/', domain=None, httponly=True, samesite='Lax')

    @staticmethod
    def __get_userinfo():
        access_token = request.cookies.get('access-token')
        try:
            payload = check_access_token(access_token)
            if 'https://api.openai.com/auth' not in payload or 'https://api.openai.com/profile' not in payload:
                raise Exception('invalid access token')
        except:
            return True, None, None, None, None

        user_id = payload['https://api.openai.com/auth']['user_id']
        email = payload['https://api.openai.com/profile']['email']

        return False, user_id, email, access_token, payload

    @staticmethod
    def chat_index(conversation_id=None):
        resp = redirect('/')

        return resp

    def logout(self):
        resp = redirect(url_for('login'))
        self.__set_cookie(resp, '', 0)

        return resp

    def login(self):
        template = 'login_full.html' if self.login_local else 'login.html'
        return render_template(template, api_prefix=self.api_prefix)

    def login_post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        mfa = request.form.get('mfa')
        error = None

        if username and password:
            try:
                access_token = Auth0(username, password,
                                     self.proxy,mfa=mfa).auth(self.login_local)
                payload = check_access_token(access_token)

                resp = make_response('please wait...', 302)
                resp.headers.set('Location', '/')
                self.__set_cookie(resp, access_token, payload['exp'])

                return resp
            except Exception as e:
                error = str(e)

        template = 'login_full.html' if self.login_local else 'login.html'
        return render_template(template, username=username, error=error, api_prefix=self.api_prefix)

    def login_token(self):
        access_token = request.form.get('access_token')
        error = None

        if access_token:
            try:
                payload = check_access_token(access_token)

                resp = jsonify({'code': 0, 'url': '/'})
                self.__set_cookie(resp, access_token, payload['exp'])

                return resp
            except Exception as e:
                error = str(e)

        return jsonify({'code': 500, 'message': 'Invalid access token: {}'.format(error)})

    def chat(self, conversation_id=None):
        err, user_id, email, _, _ = self.__get_userinfo()
        if err:
            return redirect(url_for('login'))

        query = request.args.to_dict()
        if conversation_id:
            query['chatId'] = conversation_id

        props = {
            'props': {
                'pageProps': {
                    'user': {
                        'id': user_id,
                        'name': email,
                        'email': email,
                        'image': None,
                        'picture': None,
                        'groups': [],
                    },
                    'serviceStatus': {},
                    'userCountry': 'US',
                    'geoOk': True,
                    'serviceAnnouncement': {
                        'paid': {},
                        'public': {}
                    },
                    'isUserInCanPayGroup': True
                },
                '__N_SSP': True
            },
            'page': '/c/[chatId]' if conversation_id else '/',
            'query': query,
            'buildId': self.build_id,
            'isFallback': False,
            'gssp': True,
            'scriptLoader': []
        }

        template = 'detail.html' if conversation_id else 'chat.html'
        return render_template(template, pandora_sentry=self.sentry, api_prefix=self.api_prefix, props=props)

    def session(self):
        err, user_id, email, access_token, payload = self.__get_userinfo()
        if err:
            return jsonify({})

        ret = {
            'user': {
                'id': user_id,
                'name': email,
                'email': email,
                'image': None,
                'picture': None,
                'groups': [],
            },
            'expires': datetime.utcfromtimestamp(payload['exp']).isoformat(),
            'accessToken': access_token,
            'authProvider': 'auth0'
        }

        return jsonify(ret)

    def chat_info(self, conversation_id=None):
        err, user_id, email, _, _ = self.__get_userinfo()
        if err:
            return jsonify({'pageProps': {'__N_REDIRECT': '/auth/login?', '__N_REDIRECT_STATUS': 307}, '__N_SSP': True})

        ret = {
            'pageProps': {
                'user': {
                    'id': user_id,
                    'name': email,
                    'email': email,
                    'image': None,
                    'picture': None,
                    'groups': [],
                },
                'serviceStatus': {},
                'userCountry': 'US',
                'geoOk': True,
                'serviceAnnouncement': {
                    'paid': {},
                    'public': {}
                },
                'isUserInCanPayGroup': True
            },
            '__N_SSP': True
        }

        return jsonify(ret)

    @staticmethod
    def check():
        ret = {
            'accounts': {
                'default': {
                    'account': {
                        'account_user_role': 'account-owner',
                        'account_user_id': 'd0322341-7ace-4484-b3f7-89b03e82b927',
                        'processor': {
                            'a001': {
                                'has_customer_object': True
                            },
                            'b001': {
                                'has_transaction_history': True
                            }
                        },
                        'account_id': 'a323bd05-db25-4e8f-9173-2f0c228cc8fa',
                        'is_most_recent_expired_subscription_gratis': True,
                        'has_previously_paid_subscription': True
                    },
                    'features': [
                        'model_switcher',
                        'model_preview',
                        'system_message',
                        'data_controls_enabled',
                        'data_export_enabled',
                        'show_existing_user_age_confirmation_modal',
                        'bucketed_history',
                        'priority_driven_models_list',
                        'message_style_202305',
                        'layout_may_2023',
                        'plugins_available',
                        'beta_features',
                        'infinite_scroll_history',
                        'browsing_available',
                        'browsing_inner_monologue',
                        'browsing_bing_branding',
                        'shareable_links',
                        'plugin_display_params',
                        'tools3_dev',
                        'tools2',
                        'debug',
                    ],
                    'entitlement': {
                        'subscription_id': 'd0dcb1fc-56aa-4cd9-90ef-37f1e03576d3',
                        'has_active_subscription': True,
                        'subscription_plan': 'chatgptplusplan',
                        'expires_at': '2089-08-08T23:59:59+00:00'
                    },
                    'last_active_subscription': {
                        'subscription_id': 'd0dcb1fc-56aa-4cd9-90ef-37f1e03576d3',
                        'purchase_origin_platform': 'chatgpt_mobile_ios',
                        'will_renew': True
                    }
                }
            },
            'temp_ap_available_at': '2023-05-20T17:30:00+00:00'
        }
        return jsonify(ret)


bot = ChatBot()
resource_path = abspath(join(dirname(__file__), 'flask'))
app = Flask(__name__, static_url_path='',
            static_folder=join(resource_path, 'static'),
            template_folder=join(resource_path, 'templates'))
app.wsgi_app = ProxyFix(app.wsgi_app, x_port=1)
app.after_request(bot.after_request)

app.route('/api/auth/session')(bot.session)
app.route('/api/accounts/check/v4-2023-04-27')(bot.check)
app.route('/auth/logout')(bot.logout)
app.route('/_next/data/{}/index.json'.format(bot.build_id))(bot.chat_info)
app.route(
    '/_next/data/{}/c/<conversation_id>.json'.format(bot.build_id))(bot.chat_info)

app.route('/')(bot.chat)
app.route('/c')(bot.chat)
app.route('/c/<conversation_id>')(bot.chat)

app.route('/chat')(bot.chat_index)
app.route('/chat/<conversation_id>')(bot.chat_index)

app.route('/auth/login')(bot.login)
app.route('/auth/login', methods=['POST'])(bot.login_post)
app.route('/auth/login_token', methods=['POST'])(bot.login_token)
