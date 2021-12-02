
import httpx
import trio

import sys, os, time
from optparse import OptionParser
from datetime import datetime
import itertools

def import_holehe():
    #just check if dependencie holehe is here
    try: 
        import holehe
        return True
    except: 
        return False

def inputs(options):
    firstname = str(input("Target Firstname: "))
    lastname = str(input("Target Last name: "))
    secondname = str(input("Target second Name: "))
    pseudo = str(input("Target pseudo: "))
    dob = input("Target date of birth (Format: ddmmyyyy): ")
    postcode = str(input("Target post code: "))
    second_mail = str(input("Target second mail: "))
    try:
        dob = str(dob)

        if len(dob) != 8 and options.birthday == "yes":
            print("Bad Format")
            exit()
        if dob.isnumeric() == False:
            dob = 0
        else:
            dob = datetime.strptime(dob, '%d%m%Y').date()
            ldob = str(dob).split('-')
            dob = ldob
    except ValueError:
        dob = 0


    values_combo = [(firstname, secondname, pseudo, lastname), dob, postcode, second_mail]
    return (values_combo)

def allItermail(names):
    combiv = []
    for names in names:
        if names != "":
            combiv += [[names, names[0]]]
        else:
            combiv += " "
    punctuations = ['-', '_', '.']
    combi = list(itertools.product(combiv[0], combiv[1], combiv[2], combiv[3], punctuations ))
    combi2 = list(itertools.product(combiv[0], combiv[1], combiv[2], combiv[3]))
    combis = [s for x in combi for s in itertools.permutations(x, 5)  if s[0] not in punctuations if s[:-1] not in punctuations]

    combis.extend(["".join(s) for x in combi2
                        for s in itertools.permutations(x, 4)
                        if s[0] not in punctuations
                        if s[-1] not in punctuations
                        ])

    combis = ["".join(s) for s in combis]
    namesf = []
    for name in names:
        if name != "":
            namesf.append(name)
    if len(namesf) > 0:
        combis.extend(namesf)
    final_combi = list()

    for combi in combis:
        if " " in combi:
            combi = combi.replace(" ", "")
        final_combi.append(combi)
    final_combi = list(set(filter(lambda x: len(x) > 4, final_combi)))
    final_combi = list(set(filter(lambda x: x[0] != '-' and x[0] != '_' and x[0] != '.', final_combi)))
    final_combi = list(set(filter(lambda x: x[-1] != '-' and x[-1] != '_' and x[-1] !='.', final_combi)))
    return final_combi

def simpleItermail(names):

    combiv = []
    final_iter = list()
    if names[0] != "":
        combiv += [[names[0], names[0][0]]]
    else:
        combiv += " "
    if names[3] != "":
        combiv += [[names[3], names[3][0]]]
    else:
        combiv += " "

    punctuations = ['-', '_', '.']
    combi = list(itertools.product(combiv[0], combiv[1],punctuations ))
    combi2 = list(itertools.product(combiv[0], combiv[1]))
    combis = [s for x in combi for s in itertools.permutations(x, 3)  if s[0] not in punctuations if s[:-1] not in punctuations]
    combis.extend(["".join(s) for x in combi2
                        for s in itertools.permutations(x, 2)
                        if s[0] not in punctuations
                        if s[-1] not in punctuations])

    combis = ["".join(s) for s in combis]
    if names[0] != "":
        if names[3] != "":
            combis.extend([names[0], names[3]])
        else:
            combis.extend([names[0]])
    if names[3] != "" and names[0] == "":
        combis.extend([names[3]])

    combis = list(set(filter(lambda x : len(x) > 4, combis)))
    combis = list(set(filter(lambda x : x[0] not in '-_.' and x[-1] not in '_-.', combis)))
    return (combis)

def create_mail(base_mails, number):
    probable_mail = list()
    for base in base_mails:
        probable_mail.append(base)
        x = 1
        while x <= number:
            probable_mail.append(base+str(x))
            x += 1
    return (probable_mail)

async def valid_mail(mail, client, final_mail):
    url = f'https://mail.google.com/mail/gxlu?email={mail}'
    try:
        response = await client.get(url)
        if 'set-cookie' in response.headers:
            final_mail.append(f'{mail}')
            print(f'Valid mail : {mail}')
    except:
        pass
    return final_mail

async def launch_check(mail, client, final_mail):
    await valid_mail(mail, client, final_mail)

async def check_mail(mail, final_mail):
    start_time = time.time()
    client = httpx.AsyncClient(timeout=10)

  
    async with trio.open_nursery() as nursery:
        for m in mail:
            nursery.start_soon(launch_check, m, client, final_mail)

    await client.aclose()
    return (final_mail)

def write_final(final_mail, combos_values):
    file_name = ""
    for combo in combos_values[0]:
        if combo != "":
            file_name+=str(combo)
    if file_name == "":
        file_name = "output_existing.txt"
    else:
        file_name = f'{file_name}_existing.txt'
    with open(file_name, 'a') as f:
        for mail in final_mail:
            f.write(mail+"\n")

def comboBirthPart(dob):
    combos = list()
    combos1 = list(itertools.product(dob[0], dob[1], dob[2]))
    combos =[s for x in combos1 for s in itertools.permutations(x,3)]
    combos.extend([s for x in combos1 for s in itertools.permutations(x, 2)])
    combos = list(set(combos))
    return(combos)

def createMailBirthday(base_mail, dob):
    maildob = list()
    combos = list()
    dobstr = list()
    dobstr2 = list()
    for d in dob:
        dobstr.append([str(d)])
        dobstr2.append([str(d)])
    dobstr2[0] = [dob[0][2:]]
    combos.extend(comboBirthPart(dobstr))
    combos.extend(comboBirthPart(dobstr2))

    combo_dob = ["".join(s) for s in combos]
    combo_dob = list(set(combo_dob))
    for mail in base_mail:
        for date in combo_dob:
            maildob += [mail+date, date+mail]
    return (maildob)

def createMailPostCode(base_mail, postcode):
    lpostcode = list()
    for base in base_mail:
        lpostcode.append(base+str(postcode))
        lpostcode.append(str(postcode)+base)
    return(lpostcode)

def addProvider(base_mail, providers):
    providermail = list()
    mail = list()
    for provider in providers:
        if "gmail" in provider:
            mail = list(set(filter(lambda x: '-' not in x and "_" not in x, base_mail)))
            mail = list(set(filter(lambda x: '.' not in x, base_mail)))
            for m in mail:
                providermail.append(f'{m.lower()}@{provider.lower()}')
        else:
            for m in base_mail:
                providermail.append(f"{m.lower()}@{provider.lower()}")

    return providermail

async def maincore():
    parser = OptionParser()

    parser.add_option("-s", "--simple", dest="simple", type="int",
                        help= """Search only simple combinations without number.\n Options:\n\n
0 - only name + surname without separator, 1 - name + surname + separator,      2 - all combinaisons """)

    parser.add_option("-o", "--occurence", dest="occurence", type="int",
                        help="Define the number of mail to search. Default : 2021")
    parser.add_option("-b", "--birthday", dest="birthday", default="False",
                        help="Search simple combinations with date of birthday")

    parser.add_option("-p", "--provider", dest="provider", type="str", help="Create list of mail from a special provider. Gmail by default.")
    parser.add_option('-H', "--holehe", dest="holehe", type="str", help="Call the holehe modules to check where the mail exists")


    (options, args) = parser.parse_args()

    combos_values = inputs(options)
    probable_mail = list()
    final_mail = list()
    providers = list()


    if options.simple == 0:
        base_mail = (combos_values[0][0]+combos_values[0][3], combos_values[0][3]+combos_values[0][0])
    elif options.simple == 1:
        base_mail = simpleItermail(combos_values[0])
        number = 0
    else:
        base_mail = allItermail(combos_values[0])

    if options.occurence:
        number = options.occurence
    else:
        number = 2021

    if options.provider:
        while 1:
            provider = (input("Enter a provider name (format provider.extension - Enter 'Stop' to finish):\n"))
            if provider == "stop":
                break
            providers.append(provider)
    providers.append("gmail.com")

    if combos_values[2] != "":
        probable_mail.extend(createMailPostCode(base_mail, combos_values[2]))

    if options.birthday == "yes" and combos_values[1]:
        probable_mail.extend(createMailBirthday(base_mail, combos_values[1]))
    probable_mail.extend(create_mail(base_mail, number))
    probable_mail = addProvider(probable_mail, providers)


    if combos_values[3] != "":
        probable_mail.append(combos_values[3])

    final_mail = await check_mail(probable_mail, final_mail)
    if options.holehe == "yes":
        if(import_holehe()):
            for mail in final_mail:
                os.system(f'holehe --only-used {mail}')
        else:
            print("holehe not found, please install holehe dependencie (https://github.com/megadose/holehe)")


    write_final(final_mail, combos_values)

if __name__ == "__main__":
    trio.run(maincore)
