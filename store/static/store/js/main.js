// Глобальная функция обновления счётчика корзины
function updateCartCount() {
    fetch('/cart/count/')   // ← абсолютный путь, так как URL корня /cart/count/
        .then(response => response.json())
        .then(data => {
            const cartCountEl = document.getElementById('cartCount');
            if (cartCountEl) {
                cartCountEl.textContent = data.count;
            }
        })
        .catch(error => console.error('Ошибка получения счетчика корзины:', error));
}

function showToast(message, type = 'success') {
    const toastEl = $('#liveToast');
    toastEl.removeClass('text-bg-success text-bg-danger text-bg-warning text-bg-info');
    const classMap = {
        'success': 'text-bg-success',
        'error': 'text-bg-danger',    // ← красный фон
        'warning': 'text-bg-warning',
        'info': 'text-bg-info'
    };
    toastEl.addClass(classMap[type] || 'text-bg-success');
    $('#toastMessage').text(message);
    toastEl.toast('show');
}

$(document).ready(function () {

    setTimeout(function () {
        $('.pagination').css({ 'display': 'flex', 'visibility': 'visible', 'opacity': '1' });
    }, 100);

    // Обновляем счётчик корзины при загрузке
    updateCartCount();

    let isLoading = false;
    let currentPage = 1;

    // Функция загрузки комиксов через AJAX
    function loadComics(urlParams = '') {
        if (isLoading) return;
        isLoading = true;
        $('#loadingIndicator').show();
        $('#comicsContainer').css('opacity', '0.5');

        let url = '/filter/' + (urlParams ? '?' + urlParams : '');
        if (currentPage > 1) {
            url += (urlParams ? '&' : '?') + 'page=' + currentPage;
        }

        $.ajax({
            url: url,
            method: 'GET',
            success: function (data) {
                $('#comicsContainer').html(data.html).css('opacity', '1');
                if (urlParams) {
                    history.pushState(null, '', '?' + urlParams);
                } else {
                    history.pushState(null, '', window.location.pathname);
                }
                attachPaginationEvents();
                isLoading = false;
                $('#loadingIndicator').hide();
            },
            error: function () {
                alert('Ошибка загрузки данных');
                isLoading = false;
                $('#loadingIndicator').hide();
                $('#comicsContainer').css('opacity', '1');
            }
        });
    }

    function attachPaginationEvents() {
        $('.pagination .page-link').click(function (e) {
            e.preventDefault();
            let page = $(this).data('page');
            if (page) {
                currentPage = page;
                let formData = $('#filterForm').serialize();
                loadComics(formData);
            }
        });
    }

    $('#filterForm').on('submit', function (e) {
        e.preventDefault();
        currentPage = 1;
        let formData = $(this).serialize();
        loadComics(formData);
    });

    $('#resetFilters').click(function () {
        $('#filterForm')[0].reset();
        currentPage = 1;
        loadComics('');
    });

    // Мгновенный поиск при вводе текста (с задержкой 500 мс)
    let searchTimeout;
    $('#searchInput').on('input', function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
            currentPage = 1;
            let formData = $('#filterForm').serialize();
            loadComics(formData);
        }, 100);
    });


    // Автоматическое применение фильтров при изменении любых полей
    $('#filterForm').on('change', 'select, input[type="checkbox"]', function () {
        currentPage = 1;
        let formData = $('#filterForm').serialize();
        loadComics(formData);
    });

    // Для текстового поиска — с задержкой (уже есть)
    // Для числовых полей (мин/макс цена) — с задержкой, чтобы не дёргать на каждую цифру
    let priceTimeout;
    $('#minPrice, #maxPrice').on('input', function () {
        clearTimeout(priceTimeout);
        priceTimeout = setTimeout(function () {
            currentPage = 1;
            let formData = $('#filterForm').serialize();
            loadComics(formData);
        }, 600);
    });

    // Кнопка скрытия/показа фильтров (исправленная)
    $('#toggleFiltersBtn').click(function () {
        let sidebar = $('#filterSidebar');
        let contentCol = $('#contentCol');
        let btn = $(this);

        if (sidebar.is(':visible')) {
            sidebar.hide();
            contentCol.removeClass('col-lg-9 col-md-8').addClass('col-12');
            btn.html('<i class="fas fa-chevron-right"></i> Показать фильтры');
        } else {
            sidebar.show();
            contentCol.removeClass('col-12').addClass('col-lg-9 col-md-8');
            btn.html('<i class="fas fa-chevron-left"></i> Скрыть фильтры');
        }
    });

    // Быстрый просмотр
    $(document).on('click', '.quick-view-btn', function () {
        let comicId = $(this).data('id');
        $.get('/quick-view/' + comicId + '/', function (data) {
            $('#quickViewContent').html(data.html);
            $('#quickViewModal').modal('show');
        });
    });

    attachPaginationEvents();

    let urlParams = new URLSearchParams(window.location.search);
    if (urlParams.toString()) {
        $('#searchInput').val(urlParams.get('search') || '');
        $('#categorySelect').val(urlParams.get('category') || '');
        $('#publisherSelect').val(urlParams.get('publisher') || '');
        $('#minPrice').val(urlParams.get('min_price') || '');
        $('#maxPrice').val(urlParams.get('max_price') || '');
        $('#inStock').prop('checked', urlParams.get('in_stock') === 'on');
        currentPage = parseInt(urlParams.get('page')) || 1;
        loadComics(urlParams.toString());
    }
});



// AJAX-добавление в корзину (для кнопок с классом .add-to-cart-btn)
$(document).on('click', '.add-to-cart-btn', function (e) {
    e.preventDefault();
    let url = $(this).attr('href');
    let btn = $(this);
    btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>');

    $.ajax({
        url: url,
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        success: function (data) {
            if (data.success) {
                updateCartCount(); // обновит счётчик
                // Показываем уведомление (можно использовать Bootstrap Toast)
                showToast(data.message); // или более красивое оповещение
            }
        },
        error: function () {
            showToast('Ошибка при добавлении в корзину');
        },
        complete: function () {
            btn.prop('disabled', false).html('<i class="fas fa-cart-plus"></i> В корзину');
        }
    });
});

// AJAX-удаление из корзины (на странице cart_detail)
// Удаление из корзины с подтверждением
// Удаление из корзины с подтверждением
let pendingRemoveUrl = null;
let pendingRemoveRow = null;

$(document).on('click', '.remove-from-cart-btn', function(e) {
    e.preventDefault();
    pendingRemoveUrl = $(this).attr('href');
    pendingRemoveRow = $(this).closest('tr');
    $('#confirmModalBody').text('Вы действительно хотите удалить этот товар из корзины?');
    $('#confirmModal').modal('show');
});

$('#confirmModalBtn').click(function() {
    if (pendingRemoveUrl) {
        $.ajax({
            url: pendingRemoveUrl,
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'},
            success: function(data) {
                if (data.success) {
                    pendingRemoveRow.remove();
                    updateCartCount();
                    recalculateCartTotal();   // ← пересчитываем сумму
                    showToast(data.message, 'error');
                }
                $('#confirmModal').modal('hide');
                pendingRemoveUrl = null;
                pendingRemoveRow = null;
            },
            error: function() {
                showToast('Ошибка при удалении', 'error');
                $('#confirmModal').modal('hide');
                pendingRemoveUrl = null;
                pendingRemoveRow = null;
            }
        });
    }
});

// Функция пересчёта итоговой суммы корзины
function recalculateCartTotal() {
    let total = 0;
    $('.cart-item-total').each(function() {
        let text = $(this).text().replace(/[^0-9.,]/g, '').replace(',', '.');
        let value = parseFloat(text);
        if (!isNaN(value)) {
            total += value;
        }
    });
    $('#cartTotal').text(total.toFixed(2) + ' ₽');
}
