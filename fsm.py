#-*- coding: utf-8 -*-　　 
#-*- coding: cp950 -*-　
from transitions.extensions import GraphMachine


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    def reset_init(self, update):
        text = update.message.text
        return text.lower() == '/start'

############################################################### ask poem
    def is_going_to_state_get_poem(self, update):
        text = update.message.text
        return text.lower() == 'get poem'

    def success(self, update):
        text = update.message.text
        return text.lower() == 'success'

    def on_enter_state_echo_poem(self, update):
        self.go_back(update)

    def failed(self, update):
        text = update.message.text
        return text.lower() == 'failed'

    def on_enter_state_again(self, update):
        self.go_back(update)

############################################################### get num
    def is_going_to_state_get_num(self, update):
        text = update.message.text
        return text.lower() == 'get num'

    def on_enter_state_get_num(self, update):
        self.init_list(update)

    def full(self, update):
        text = update.message.text
        return text.lower() == 'list full'

    def on_enter_state_echo_list(self, update):
        self.go_back(update)

    def not_full(self, update):
        text = update.message.text
        return text.lower() == 'list not full'

############################################################### secret
    def is_going_to_state_echo_link(self, update):
        text = update.message.text
        return text.lower() == 'Hi'

    def on_enter_state_echo_link(self, update):
        self.init_list(update)

############################################################### parser
    def is_going_to_state_parse(self, update):
        text = update.message.text
        return text.lower() == 'start parse'

    def on_enter_state_parse(self, update):
        self.start_parse(update)

    def on_enter_state_echo_movie_time(self, update):
        self.go_back(update)

############################################################### help
    def is_going_to_state_help(self, update):
        text = update.message.text
        return text.lower() == '/help'

    def on_enter_state_help(self, update):
        self.go_back(update)

############################################################### other
    def is_going_to_state_other(self, update):
        text = update.message.text
        return text.lower() == 'other'

    def on_enter_state_get_num(self, update):
        self.init_list(update)
