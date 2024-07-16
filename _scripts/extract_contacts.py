import os
import textwrap


CURRENT_DIR = os.path.dirname(__file__)

AUTHORS = [
    {
        'NAME': 'Francesca Chiusaroli',
        'EMAIL': 'f.chiusaroli@unimc.it',
        'IMG_URL': '/assets/img/fc.jpg',
        'WEBSITE': 'https://docenti.unimc.it/f.chiusaroli',
        'DESCRIPTION_IT': textwrap.dedent(\
            """\
            Professoressa ordinaria di Linguistica Generale e Applicata e Linguistica dei Media presso l'Università di Macerata (Italia). Ha precedentemente insegnato presso le Università di Udine e Roma "Tor Vergata". Tra i suoi interessi di ricerca figurano le scritture, sia da prospettive teoriche che storiche, le pasigrafie e le stenografie. È l'autrice del progetto di ricerca interdisciplinare "Scritture Brevi" (dal 2009) e del blog dedicato <a href="https://www.scritturebrevi.it">scritturebrevi</a> e di una vivace comunità su Twitter (#scritturebrevi). È l'ideatrice dell'Emojitaliano e supervisiona le sue traduzioni, a cominciare da Pinocchio in Emojitaliano. Ha concepito l'Emojitaliano come un codice per la comunicazione ausiliaria internazionale, credendo che il potere del popolare repertorio pittografico digitale, unito all'istituzione di glossari e grammatiche convenzionali condivise attraverso il crowdsourcing, possa fungere da codice mediatore capace di superare le barriere linguistiche e semplificare la comunicazione."""
        ),
        'DESCRIPTION_EN': textwrap.dedent(\
            """\
            Full professor of General and Applied Linguistics and Media Linguistics at the University of Macerata (Italy). She has previously taught at the Universities of Udine and Rome "Tor Vergata." Among her research interests are writings, both in theoretical and historical perspectives, pasigraphies and shorthands. She is the author of the interdisciplinary research project "Scritture Brevi"(since 2009) and the devoted blog <a href="https://www.scritturebrevi.it">scritturebrevi</a> and an active community on Twitter (#scritturebrevi). She is the inventor of Emojitaliano and oversees its translations, starting with Pinocchio in Emojitaliano. She conceived Emojitaliano as a code for international auxiliary communication, believing that the power of the popular digital pictographic repertoire, combined with the establishment of conventional glossaries and grammar as shared in crowdsourcing, can serve as a mediating code capable of overcoming language barriers and simplifying communication."""
        ),
    },
    {
        'NAME': 'Johanna Monti',
        'EMAIL': 'jmonti@unior.it',
        'IMG_URL': '/assets/img/jm.jpg',
        'WEBSITE': 'https://unifind.unior.it/resource/person/2569',
        'DESCRIPTION_IT': textwrap.dedent(\
            """\
            Professoressa ordinaria di Studi sulla Traduzione e Traduzione Specializzata presso l'Università di Napoli "L'Orientale", ha insegnato precedentemente presso l'Università di Sassari. I suoi interessi di ricerca si concentrano principalmente sulle tecnologie della traduzione, la traduzione automatica e l'IA. È stata coinvolta nel progetto Emojitaliano fin dalla sua nascita, contribuendo alle attività di traduzione e, in particolare, supervisionando pubblicazioni scientifiche sugli aspetti linguistici dell'automazione e delle tecnologie per la traduzione assistita da computer a livello internazionale."""
        ),
        'DESCRIPTION_EN': textwrap.dedent(\
            """\
            Full professor of Translation Studies and Specialized Translation at the University of Naples "L'Orientale", previously taught at the University of Sassari. Her research interests primarily focus on translation technologies, machine translation, and AI. She has been involved in the Emojitaliano project since its birth, contributing to the translation tasks and, in particular, overseeing scientific publications on linguistic aspects of automation and technologies for computer-assisted translation on an international level."""
        ),
    },
    {
        'NAME': 'Federico Sangati',
        'EMAIL': 'federico.sangati@gmail.com',
        'IMG_URL': '/assets/img/fs.jpg',
        'WEBSITE': 'https://fede.sangati.me',
        'DESCRIPTION_IT': textwrap.dedent(\
            """\
            Attualmente lavora come Tecnico di Ricerca presso l'Unità di Ricerca in Neurorobotica Cognitiva presso l'Okinawa Institute of Science and Technology in Giappone, dove supporta ricerche in vari campi come la robotica, l'elaborazione del linguaggio naturale, le simulazioni informatiche e l'interazione uomo-computer. Dal 2015 esplora attivamente il campo dell'IA conversazionale e ha sviluppato diversi ChatBot. Con la sua esperienza in questi campi, si è entusiasticamente unito al progetto originale Emojitaliano fin dalla sua nascita, assumendosi l'incarico di creare l'<a href="https://t.me/emojitalianobot">@emojitalianobot</a>, fornendo così il supporto tecnologico cruciale che preserva e rende disponibile alla comunità il glossario, la grammatica e giochi per comprendere l'Emojilingo."""
        ),
        'DESCRIPTION_EN': textwrap.dedent(\
            """\
            Currently working as a Research Technician in the Cognitive Neurorobotics Research Unit at the Okinawa Institute of Science and Technology in Japan, where he supports researches in a variety of fields such as Robotics, Natural Language Processing, Computer Simulations, and Human-Computer Interaction. Since 2015 he has been actively exploring the field of conversational AI and developed a number of ChatBots. With his expertise in these fields, he enthusiastically joined the original Emojitaliano project from its birth, taking charge of creating the <a href="https://t.me/emojitalianobot">@emojitalianobot</a>, therefore providing the crucial technological support which preserves and makes available to the community the glossary, grammar, and entertaining games with Emojilingo."""
        ),
    },
]


AUTHOR_TEMPLATE = lambda name, email, img_url, website, description: \
    textwrap.dedent(
    f"""\
        <tr>
            <td colspan=2 align="left"><h1>{name}</h1></td>
        </tr>
        <tr>
            <td style="vertical-align:middle" align="center">
                <p>
                    <img class="contact-img" src="{img_url}">
                </p>
                <p>
                    <a class="emojilink" href="{website}" target="_blank">
                        <span>🌐</span>
                    </a>
                    <a class="emojilink" href="mailto:{email}">
                        <span>📧</span>
                    </a>
                </p>
            </td>
            <td align="left">
                <p>
                    {description}
                </p>
            </td>
        </tr>
    """
)

def extract_contacts():
    for lang in ['it','en']:
        contact_file_lang = f'_i18n/{lang}/contacts.html'
        html_content = []
        html_content.extend([
            '<table class="contacts">',
                '<tbody>'
        ])
        for author_dict in AUTHORS:
            html_content.append(
                AUTHOR_TEMPLATE(
                    author_dict['NAME'],
                    author_dict['EMAIL'],
                    author_dict['IMG_URL'],
                    author_dict['WEBSITE'],
                    author_dict[f'DESCRIPTION_{lang.upper()}'],
                )
            )
            html_content.extend([
                '<tr></tr>',
            ])

        html_content.extend([
            '</tbody>',
            '</table>',
        ])

        with open(contact_file_lang, 'w') as f:
            f.write('\n'.join(html_content))

if __name__ == "__main__":
    extract_contacts()