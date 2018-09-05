from mongoengine import *
from quads.helpers import param_check

connect('quads')


class Cloud(Document):
    cloud = StringField()
    description = StringField()
    owner = StringField()
    ticket = StringField()
    qinq = BooleanField()
    wipe = BooleanField()
    post_config = ListField()
    ccuser = ListField()

    @staticmethod
    def prep_data(data):
        defaults = {'owner': 'nobody',
                    'ccuser': [],
                    'ticket': '000000',
                    'qinq': False,
                    'wipe': True}

        result, data = param_check(data,
                                   ['cloud', 'description', 'owner', 'ccuser',
                                    'ticket', 'qinq', 'wipe'],
                                   defaults)

        return result, data


class Host(Document):
    host = StringField()
    cloud = ReferenceField(Cloud, required=True)
    interfaces = DictField()
    schedule = ListField(DictField())
    type = StringField()

    @staticmethod
    def prep_data(data):
        result, data = param_check(data, ['host', 'cloud', 'type'])
        if not result:
            cloud = Cloud.objects(cloud=data['cloud']).first()
            if not cloud:
                result.append('Cloud %s not found' % data['cloud'])
            else:
                data['cloud'] = cloud

        return result, data

    @staticmethod
    def prep_schedule_data(data):
        result, data = param_check(data, ['cloud', 'host',
                                          'start', 'end'])
        host = None
        if not result:
            cloud = Cloud.objects(cloud=data['cloud']).first()
            host = Host.objects(host=data['host']).first()
            if not cloud:
                result.append('Cloud %s not found' % data['cloud'])
            elif not host:
                result.append('Host %s not found' % data['host'])
            else:
                data['cloud'] = cloud
                del data['host']

            data = {'add_to_set__schedule': [data]}

        return result, host, data

    @staticmethod
    def prep_interfaces_data(data):
        result, data = param_check(data, ['host', 'interface', 'mac',
                                          'vendor_type', 'port'])
        host = None
        if not result:
            host = Host.objects(host=data['host']).first()
            if not host:
                result.append('Host %s not found' % data['host'])
            else:
                del data['host']
            interface = data['interface']
            del data['interface']
            data = {'set__interfaces__%s' % interface: data}

        print(result)

        return result, host, data


class History(Document):
    pass


class CloudHistory(Document):
    cloud = ReferenceField(Cloud, required=True)
    dt_stamp = DateTimeField()
    name = StringField()
    description = StringField()
    owner = StringField()
    ticket = StringField()
    qing = BooleanField()
    wipe = BooleanField()
    post_config = ListField()
    ccusers = ListField()
