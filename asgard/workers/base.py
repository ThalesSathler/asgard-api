class Autoscaler():
    def should_scale(self, labels):
        meets_criteria = False

        if 'asgard.autoscale.ignore' in labels:
            ignores = labels['asgard.autoscale.ignore']
        else:
            ignores = ''

        if 'all' in ignores:
            return False

        if 'asgard.autoscale.cpu' in labels:
            if 'cpu' not in ignores:
                meets_criteria = True
        elif 'asgard.autoscale.mem' in labels:
            if 'mem' not in ignores:
                meets_criteria = True

        return meets_criteria
