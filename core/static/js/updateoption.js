function tipoConta() {
        // seleciona o primeiro select
        var selectConta = document.getElementById('categoria');
        // seleciona o segundo select
        var selectTaxa = document.getElementById('taxa');

        // quando o evento é disparado no primeiro select, ele exclui as options anteriores do segundo select
        while (selectTaxa.firstChild) {
          selectTaxa.removeChild(selectTaxa.firstChild);
        }

        // se a opção do select for cartão de crédito
        if (selectConta.value === '1') {
          var select = document.createElement('select');
          // cria um elemento html de option
          var option1 = document.createElement('option');
          // seta o value do option
          option1.value = 'subOption1';
          // seta o texto inserido no option
          option1.text = 'Subopção 1';
          // adiciona a option dentro do segundo select
          selectTaxa.add(option1);

          // aqui é a mesma coisa, só repete os passos acima
          var option2 = document.createElement('option');
          option2.value = 'subOption2';
          option2.text = 'Subopção 2';
          selectTaxa.add(option2);

          // caso contrario, se a segunda opção for selecionada no primeiro select
        } else if (selectConta.value === '2') {
          // aqui também é a mesma coisa, só repete os passos acima
          var option1 = document.createElement('option');
          option1.value = 'subOption3';
          option1.text = 'Subopção 3';
          selectTaxa.add(option1);

          var option2 = document.createElement('option');
          option2.value = 'subOption4';
          option2.text = 'Subopção 4';
          selectTaxa.add(option2);
        }
      }
