
class AlertBot:
    ALERT_BLOCK = {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": "Here is the result from Rocket League Item Shop Rotation. Go spend your money:money_with_wings:",
        },
    }

    def __init__(self, channel, data):
        self.channel = channel

        if type(data) != list: 
            raise TypeError('data type passed in AlertBot should be list')
        else:
            self.data = data        


    def _parse_result(self):

        formatted_text = ''

        for item in self.data:
            item_descipription = f'\n- *{item["name"]}* ({item["category"]}): {item["credits"]} credits\n'
            formatted_text += item_descipription
        
        return {
            'type': 'section', 'text':{'type': 'mrkdwn', 'text': formatted_text}
        }


    def get_message_payload(self):
        return {
            'channel': self.channel,
            'text': 'An item on your watchlist is in the shop:racing_car:',
            'blocks': [
                self.ALERT_BLOCK,
                self._parse_result()
            ]
        }
