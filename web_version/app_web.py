from flexx import flx
import requests

class AccessibilityApp(flx.Widget):
    def init(self):
        with flx.VBox():
            # Seção de Formulário
            with flx.HBox():
                self.street_name = flx.LineEdit(title='Nome da Rua:')
                self.cep = flx.LineEdit(title='CEP:')
                self.problem_type = flx.ComboBox(title='Tipo de Problema:', options=['Calçada Quebrada', 'Ausência de Rampa', 'Falta de Faixa de Pedestre', 'Outros'])
                self.severity = flx.ComboBox(title='Gravidade:', options=['Baixa', 'Média', 'Alta'])
                self.report_button = flx.Button(text='Registrar Rua')
                self.view_map_button = flx.Button(text='Visualizar no Mapa')

            # Seção de Filtros
            with flx.HBox():
                self.filter_problem_type = flx.ComboBox(title='Filtrar por Tipo de Problema:', options=['Todos', 'Calçada Quebrada', 'Ausência de Rampa', 'Falta de Faixa de Pedestre', 'Outros'])
                self.filter_severity = flx.ComboBox(title='Filtrar por Gravidade:', options=['Todos', 'Baixa', 'Média', 'Alta'])
                self.filter_button = flx.Button(text='Filtrar Problemas')

            # Seção de Tabela
            self.problem_table = flx.TableWidget(
                ncolumns=6,
                column_headers=['ID', 'Nome da Rua', 'CEP', 'Tipo de Problema', 'Gravidade', 'Status'],
                editable=False
            )
            self.update_table()
            self.message_label = flx.Label(text='')

    @flx.reaction('report_button.pointer_click')
    def register_problem(self, *events):
        # Função para registrar um problema
        street_name = self.street_name.text
        cep = self.cep.text
        problem_type = self.problem_type.text
        severity = self.severity.text

        # Aqui você pode adicionar a lógica para inserir no banco de dados, por exemplo, usando uma API
        response = requests.post('http://localhost/register_problem', data={
            'street_name': street_name,
            'cep': cep,
            'problem_type': problem_type,
            'severity': severity
        })
        if response.status_code == 200:
            self.message_label.set_text('Problema registrado com sucesso!')
            self.update_table()
        else:
            self.message_label.set_text('Erro ao registrar problema.')

    @flx.reaction('view_map_button.pointer_click')
    def view_map(self, *events):
        # Função para visualizar a rua no mapa
        street_name = self.street_name.text
        # Lógica para abrir o Google Maps com o endereço correspondente
        # Exemplo simplificado para ilustrar
        flx.launch("https://www.google.com/maps/search/?api=1&query=" + street_name)

    @flx.reaction('filter_button.pointer_click')
    def filter_problems(self, *events):
        # Função para filtrar problemas no banco de dados
        problem_type = self.filter_problem_type.text
        severity = self.filter_severity.text
        # Aqui você pode adicionar a lógica para filtrar no banco de dados e atualizar a tabela
        response = requests.get('http://localhost/filter_problems', params={
            'problem_type': problem_type,
            'severity': severity
        })
        if response.status_code == 200:
            problems = response.json()
            self.update_table(problems)
        else:
            self.message_label.set_text('Erro ao filtrar problemas.')

    def update_table(self, problems=[]):
        # Atualizar a tabela com problemas registrados
        if not problems:
            response = requests.get('http://localhost/get_all_problems')
            if response.status_code == 200:
                problems = response.json()
        
        self.problem_table.set_data([[p['id'], p['street_name'], p['cep'], p['problem_type'], p['severity'], p['status']] for p in problems])

    @flx.reaction('problem_table.current_index')
    def handle_table_click(self, *events):
        # Evento ao clicar em uma linha da tabela para editar ou excluir
        row = self.problem_table.current_index
        if row is not None:
            selected_problem = self.problem_table.get_data()[row]
            # Aqui você pode adicionar lógica para editar ou excluir o registro
            print(f"Selecionado: {selected_problem}")

if __name__ == '__main__':
    flx.App(AccessibilityApp).serve('localhost', 8080)
    flx.run()
