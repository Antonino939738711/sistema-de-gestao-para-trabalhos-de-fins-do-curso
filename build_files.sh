# build_files.sh
echo "Instalando dependências..."
python3 -m pip install -r requirements.txt

echo "Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput

echo "Fazendo migrações do banco..."
python3 manage.py migrate --noinput