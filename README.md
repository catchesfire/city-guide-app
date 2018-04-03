

# Przewodnik po miescie
Aplikacja powinna posiadać bazę atrakcji dostępnych dla turystów w danym mieście.
Każda atrakcja przypisana jest do okreslonej kategorii (np. muzeum, pomnik, obiekt sakralny, itp.)
* Posiada swoje położenie,
* Czas potrzebny na jej zwiedzanie,
* Ewentualną cenę biletu wstępu,
* Opis ,
* Inne parametry.

Turysta planujący odwiedzic miasto może zaplanować indywidualną trasę zwiedzania wkładając do koszyka atrakcje, które chciałby zobaczyc.
* Aplikacja powinna wygenerować optymalny plan zwiedzania w postaci listy z opisami i mapy z zaznaczonymi atrakcjami,
* Nalezy uwzględnić czas potrzebny na przemieszczanie się pomiędzy atrakcjami.

Problemy do rozważenia: 
* Kryteria optymalności planu,
* Zapamiętywanie planów,
* Gotowe propozycje planów,
* Pobieranie planów w formacie pdf.

# Kryteria oceny projektów:

ocena dst
* aplikacja powinna działać, tzn. student powinien być w stanie uruchomić ją przynajmniej na swoim komputerze,
* aplikacja powinna realizować niektóre wymagania określone w opisie,

ocena db - to co na ocenę dst +
* aplikacja powinna realizować wszystkie wymagania określone w opisie,
* aplikacja powinna być wdrożona na zewnętrznym serwerze i/lub uruchomiona na Dockerze,

ocena bdb - to co na ocenę db +
* aplikacja powinna mieć estetyczny wygląd (elementy graficzne) i/lub aplikacja powinna być bezpieczna i zawierać testy automatyczne,
* aplikacja powinna realizować przynajmniej dwie z następujących funkcjonalności: 
    *  wysyłanie emaili, 
    * wysyłanie sms, 
    * generowanie pliku pdf, 
    * prezentacja graficznego wykresu, 
    * captcha, 
    * prezentacja mapy google lub podobnej, 
    * upload plików, 
    * prezentacja kalendarza z wydarzeniami.