import whitelist
import blacklist

def main():

    run = True

    while run:

        print("\n--Script de capa basada en reglas--")
        print("1. Whitelist")
        print("2. Blacklist")
        print("3. Salir")

        option = input("Seleccione una opción: ")

        if option == "1":
            url = input("Ingrese la URL a verificar: ")
            result = whitelist.get_page_rank(url)
            print(result)
            if result['response'][0]['page_rank_decimal'] > 7:
                print("La URL está en la whitelist y tiene un PageRank mayor a 7")
            else:
                print("La URL necesita mayor verificación debido a su bajo PageRank")

        elif option == "2":
            url = input("Ingrese la URL a verificar: ")
            result = blacklist.check_url(url)
            print(result)

            if len(result) == 0:
                print("La URL no está en la blacklist")

        elif option == "3":
            run = False
            print("Saliendo...")
            

if __name__ == "__main__":
    main()