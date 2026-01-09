# Rules

1. Kod musi działać pod Pythonem 3.12.
2. Styl dokumentacji: numpy_docstring.
3. Struktura projektu obowiązkowa:
   /domain
   /providers
   /visualization
   /gui
   /tests
4. Domain Model nie może zależeć od plików źródłowych ani pandas.
5. Provider musi zwracać Domain Model.
6. Wizualizacja działa wyłącznie na Domain Model.
7. GUI nie może parsować Excela ani używać pandas.
8. GUI woła tylko Provider → Visualization.
9. Używane biblioteki:
   - pandas (tylko w providerach)
   - seaborn (wizualizacja)
   - matplotlib (wizualizacja)
   - streamlit (GUI)
10. Obsługa flag `<` `>` musi być zachowana.
11. Parametry `units` muszą być obecne dla każdego parametru.
12. Testy muszą pokrywać provider oraz model.
13. Provider może obsługiwać dynamiczne parametry i metadane.
14. Kod musi być odporny na zmianę formatu danych źródłowych.
15. Dockerfile musi pozwolić na uruchomienie GUI przez:
    `streamlit run gui/app.py --server.address=0.0.0.0`
