document.addEventListener('DOMContentLoaded', function() {
    // Admin dashboard charts using Chart.js
    if (document.getElementById('eventsChart')) {
        fetch('/admin/api/events-stats')
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('eventsChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Events',
                            data: data.values,
                            backgroundColor: 'rgba(74, 137, 220, 0.5)',
                            borderColor: 'rgba(74, 137, 220, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            });
    }
    
    // Datepicker for event form
    if (typeof $.fn.datetimepicker !== 'undefined') {
        $('.datetimepicker').datetimepicker({
            format: 'YYYY-MM-DD HH:mm',
            icons: {
                time: 'fas fa-clock',
                date: 'fas fa-calendar',
                up: 'fas fa-arrow-up',
                down: 'fas fa-arrow-down',
                previous: 'fas fa-chevron-left',
                next: 'fas fa-chevron-right',
                today: 'fas fa-calendar-check',
                clear: 'fas fa-trash',
                close: 'fas fa-times'
            }
        });
    }
    
    // Confirm delete actions
    $('.delete-confirm').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
});