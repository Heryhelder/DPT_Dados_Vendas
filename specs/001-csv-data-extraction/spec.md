# Feature Specification: Extração de Dados CSV

**Feature Branch**: `001-csv-data-extraction`

**Created**: 2026-06-28

**Status**: Draft

**Input**: "crie um método de extração de dados que vai carregar dados de um
arquivo csv que está em um diretório e irá retornar um dataframe"

## Clarifications

### Session 2026-06-28

- Q: Como lidar com arquivos CSV maiores que 100MB? → A: Rejeitar com
  mensagem de erro clara. Arquivos até 100MB são suportados.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carregamento Padrão de CSV (Priority: P1)

Como analista de dados, quero fornecer o caminho de um arquivo CSV com
cabeçalho e delimiter padrão (vírgula, UTF-8) e receber uma tabela de
dados com os dados carregados, para iniciar o pipeline de tratamento.

**Why this priority**: É a funcionalidade mínima viável — sem ela, nenhuma
etapa seguinte do pipeline (validação, preparação, métricas) pode começar.

**Independent Test**: Pode ser testado fornecendo um CSV conhecido (10
linhas, 5 colunas) e verificando que a tabela resultante tem o mesmo
número de linhas, colunas e valores.

**Acceptance Scenarios**:

1. **Given** um arquivo CSV válido com cabeçalho e 10 linhas de dados,
   **When** a função de extração é chamada com o caminho do arquivo,
   **Then** a tabela retornada contém 10 linhas e os nomes das colunas
   do cabeçalho.
2. **Given** um arquivo CSV com valores numéricos e de texto,
   **When** a função de extração é chamada,
   **Then** colunas numéricas são reconhecidas como números e colunas de
   texto são reconhecidas como texto.

---

### User Story 2 - Parâmetros Customizados (Priority: P2)

Como analista, quero especificar parâmetros como delimitador, encoding e
tipos de coluna para carregar CSVs não padronizados, garantindo
flexibilidade para diferentes fontes de dados.

**Why this priority**: CSVs reais podem usar ponto-e-vírgula, encoding
Latin-1 ou ter colunas com tipos específicos. Sem essa flexibilidade, o
pipeline quebra em fontes não padronizadas.

**Independent Test**: Fornecer um CSV separado por ponto-e-vírgula com
encoding Latin-1 e verificar que a tabela é carregada corretamente.

**Acceptance Scenarios**:

1. **Given** um CSV separado por ponto-e-vírgula,
   **When** a função é chamada com `delimiter=';'`,
   **Then** a tabela contém as colunas separadas corretamente.
2. **Given** um CSV com encoding Latin-1 (acentuação),
   **When** a função é chamada com `encoding='latin-1'`,
   **Then** os caracteres acentuados são preservados na tabela.
3. **Given** uma coluna que deve ser interpretada como data,
   **When** a função é chamada com tipos explicitados,
   **Then** a coluna é carregada como tipo data.

---

### User Story 3 - Tratamento de Erros (Priority: P3)

Como analista, quero receber mensagens de erro claras quando o arquivo
não existe, está vazio ou é malformado, para diagnosticar problemas
rapidamente sem precisar debugar o código.

**Why this priority**: Essencial para robustez, porém o pipeline pode
funcionar sem ele em cenários controlados.

**Independent Test**: Chamar a função com um caminho inexistente e
verificar que uma exceção descritiva é lançada.

**Acceptance Scenarios**:

1. **Given** um caminho de arquivo que não existe,
   **When** a função de extração é chamada,
   **Then** uma exceção `FileNotFoundError` com mensagem clara é lançada.
2. **Given** um arquivo CSV vazio,
   **When** a função de extração é chamada,
   **Then** uma exceção com mensagem "CSV vazio" é lançada.
3. **Given** um arquivo CSV com linhas de tamanho inconsistente,
    **When** a função de extração é chamada,
    **Then** uma exceção com mensagem descritiva é lançada.
4. **Given** um arquivo CSV maior que 100MB,
    **When** a função de extração é chamada,
    **Then** uma exceção com mensagem "Arquivo excede o limite de 100MB" é lançada.

---

### Edge Cases

- Arquivo CSV com BOM (Byte Order Mark) no início
- Arquivo CSV com linhas em branco no final
- Arquivo CSV com valores nulos/missing representados como `NA`, `null`,
  ou string vazia
- Arquivo CSV com aspas escapando delimitadores no conteúdo
- Caminho de arquivo com espaços ou caracteres especiais é suportado
  (Python/Pandas lida nativamente)
- Linhas em branco no final do CSV são ignoradas (comportamento padrão
  do Pandas)
- Arquivo CSV com tamanho superior a 100MB

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE aceitar um caminho de arquivo (string) como
  entrada obrigatória
- **FR-002**: Sistema DEVE retornar uma estrutura de dados tabular com
  os dados do CSV
- **FR-003**: Sistema DEVE inferir tipos de dados automaticamente
  (numérico, texto, booleano, data) por padrão
- **FR-004**: Sistema DEVE aceitar parâmetro opcional de delimitador
  (padrão: vírgula, aceita apenas 1 caractere)
- **FR-005**: Sistema DEVE aceitar parâmetro opcional de encoding
  (padrão: UTF-8). BOM (Byte Order Mark) é ignorado automaticamente.
- **FR-006**: Sistema DEVE aceitar parâmetro opcional para especificar
  tipos de coluna
- **FR-007**: Sistema DEVE lançar `FileNotFoundError` se o arquivo não
  existir
- **FR-008**: Sistema DEVE lançar erro descritivo se o CSV estiver vazio
  (arquivo de 0 bytes ou apenas com cabeçalho sem linhas de dados)
- **FR-009**: Sistema DEVE lançar erro descritivo se o CSV for
  malformado (linhas com número inconsistente de colunas)
- **FR-010**: Sistema DEVE rejeitar arquivos maiores que 100MB com
  mensagem de erro clara
- **FR-011**: Sistema DEVE registrar logs estruturados da operação de
  extração (caminho do arquivo, linhas carregadas, duração) conforme
  constituição do projeto (Princípio V)

### Key Entities

- **Arquivo CSV**: Fonte de dados bruta. Conforme a constituição do
  projeto: "O dado bruto NUNCA DEVE ser alterado — transformações sempre
  produzem novas tabelas/arquivos"
- **Configuração de Extração**: Parâmetros que controlam a leitura
  (caminho, delimitador, encoding, dtypes)
- **Tabela de Dados**: Estrutura de saída com dados tipados e nomes de
  colunas extraídos do cabeçalho

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Carregamento de CSV de até 100MB em menos de 2 segundos em
  hardware de desenvolvimento padrão; arquivos acima de 100MB são
  rejeitados com mensagem clara. *Nota: o requisito de 2 segundos é meta
  de design — não há teste de performance no escopo desta feature.*
- **SC-002**: Tabela resultante preserva 100% das linhas e colunas do
  CSV original
- **SC-003**: Usuário consegue carregar CSVs com diferentes delimitadores
  (vírgula, ponto-e-vírgula, tab) fornecendo o parâmetro correto na
  primeira chamada
- **SC-004**: 100% dos erros de entrada (arquivo ausente, vazio,
  malformado) produzem mensagens descritivas em português
- **SC-005**: A função é implementada seguindo o ciclo TDD (teste falha →
  implementação → teste passa) conforme constituição do projeto

## Assumptions

- A função recebe o caminho de **um único arquivo CSV**, não um diretório
  para scan automático
- A primeira linha do CSV contém o cabeçalho com nomes de colunas
- Delimitador padrão é vírgula (`,`)
- Encoding padrão é UTF-8
- Valores nulos no CSV são interpretados como `NaN` pelo Pandas
- Espaços em branco (whitespace) no início/fim de colunas e valores são
  removidos automaticamente (trim automático)
- TDD obrigatório conforme Constituição (Princípio III: TDD — Testes de
  Dados Obrigatórios): o teste deve ser escrito antes da implementação
- Arquivos maiores que 100MB são rejeitados (clarificação: opção A)
