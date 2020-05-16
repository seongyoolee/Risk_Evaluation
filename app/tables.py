from flask_table import Table, Col, LinkCol

class DollarCol(Col):
    def td_format(self, content):
        return '$ ' + str(content)

class InjuryClaimTable(Table):
    id = Col('Id', show=False)
    company = Col('Company', show=False)
    injury_type = Col('Injury Type')
    injury_cause = Col('Injury Cause')
    open_or_closed = Col('Open/Closed')
    year = Col('Year')
    incurred_loss = DollarCol('Incurred Loss')
    paid_loss = DollarCol('Paid Loss')
    description = Col('Description')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))