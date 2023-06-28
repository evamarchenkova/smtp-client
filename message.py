import base64
import json
import re

from constants import BOUNDARY, SEPARATOR


class Message:
    def __init__(self, text_file, config):
        self.__config = self.__get_from_json(config)
        self.__text = self.__get_from_txt(text_file)
        self.from_field = self.__get_from_field()
        self.to_field = self.__get_to_field()
        self.subject_filed = self.__get_subject_field()
        self.attachments = self.__get_attachments()

    @staticmethod
    def __get_from_json(config):
        with open(config, encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def __get_from_txt(text_file):
        with open(text_file, encoding='utf-8') as file:
            text = ''
            pattern = r'^\.+$'
            for line in file.readlines():
                line = line.strip()
                if re.match(pattern, line):
                    text += line + '.\n'
                else:
                    text += line + '\n'
        return text

    def __get_from_field(self):
        return self.__config['from']

    def __get_to_field(self):
        return self.__config['to']

    def __get_subject_field(self):
        return self.__config['subject']

    def __get_attachments(self):
        return self.__config['attachments']

    def create_headers(self):
        return f"FROM: {self.from_field}\n" \
               f"TO: {self.to_field}\n" \
               f"SUBJECT:{self.subject_filed}\n" \
               f"MIME-Version: 1.0\n" \
               f"Content-Type: multipart/mixed;\n\tboundary={BOUNDARY}\n"

    @staticmethod
    def __wrap_attachment(attachment):
        filename = attachment
        match attachment[attachment.rfind('.') + 1:]:
            case 'jpg':
                content_type = 'image/jpeg'
            case 'png':
                content_type = 'image/png'
            case 'mp3':
                content_type = 'audio/basic'
            case 'mp4':
                content_type = 'video/mpeg'
            case 'pdf':
                content_type = 'application/pdf'
            case 'txt':
                content_type = 'text/plain'
            case 'html':
                content_type = 'text/html'
            case 'json':
                content_type = 'application/json'
            case 'xml':
                content_type = 'application/xml'
        name = attachment[attachment.rfind(SEPARATOR) + 1:] if attachment.rfind(SEPARATOR) != -1 else attachment
        with open(attachment, 'rb') as file:
            attachment = base64.b64encode(file.read()).decode()
        return f'--{BOUNDARY}\n' \
               f'Content-Disposition: attachment;\n\tfilename={filename}\n' \
               f'Content-Transfer-Encoding: base64\n' \
               f'Content-Type: {content_type};\n\tname={name}\n' \
               f'\n' \
               f'{attachment}\n'

    def create_body(self):
        body = f'--{BOUNDARY}\n' \
               f'Content-Type: text/html; charset=utf-8\n' \
               f'\n' \
               f'{self.__text}\n'
        for attachment in self.attachments:
            body += self.__wrap_attachment(attachment)
        body += f'--{BOUNDARY}--'
        return body

    def create_message(self):
        return f'{self.create_headers()}\n{self.create_body()}\n.\n'
