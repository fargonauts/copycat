style_dict = dict(foreground='white',
                  background='black')

map_options = dict(
              foreground=[('disabled', 'black'),
                            ('pressed', 'white'),
                            ('active', 'white')],
              background=[('disabled', 'black'),
                          ('pressed', '!focus', 'black'),
                          ('active', 'black')],
              highlightcolor=[('focus', 'black'),
                              ('!focus', 'black')])

def configure_style(style):
    style.configure('TButton', **style_dict)
    style.map('TButton', **map_options)
    style.configure('TLabel', **style_dict)
    #style.configure('TEntry', **style_dict)
    #style.map('TEntry', **map_options)

    # A hack to change entry style
    style.element_create("plain.field", "from", "clam")
    style.layout("EntryStyle.TEntry",
		   [('Entry.plain.field', {'children': [(
		     'Entry.background', {'children': [(
		     'Entry.padding', {'children': [(
	             'Entry.textarea', {'sticky': 'nswe'})],
		      'sticky': 'nswe'})], 'sticky': 'nswe'})],
		      'border':'2', 'sticky': 'nswe'})])
    style.configure("EntryStyle.TEntry",
		     background="black", 
		     foreground="white",
		     fieldbackground="black")
