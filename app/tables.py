from flask_table import Table, Col, LinkCol
 
class InjuryClaimTable(Table):
    id = Col('Id', show=False)
    company = Col('Company', show=False)
    injury_type = Col('Injury Type')
    injury_cause = Col('Injury Cause')
    open_or_closed = Col('Open/Closed')
    year = Col('Year')
    incurred_loss = Col('Incurred Loss')
    paid_loss = Col('Paid Loss')
    description = Col('Description')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))