import os
import uuid
from flask import render_template, request, redirect, url_for, session, flash, jsonify, send_file
from app import app, db
from models import HealthReport
from openai_service import generate_health_report
from pdf_generator import generate_pdf_report

# Kaspi payment configuration
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') else os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]

@app.route('/')
def index():
    """Landing page with coach Alex introduction"""
    return render_template('index.html')

@app.route('/questionnaire')
def questionnaire():
    """Health questionnaire form"""
    # Generate unique session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('questionnaire.html')

@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    """Process questionnaire submission and generate free report"""
    try:
        # Get form data
        user_data = {
            'age': int(request.form.get('age', 0)),
            'gender': request.form.get('gender', ''),
            'weight': int(request.form.get('weight', 0)),
            'height': int(request.form.get('height', 0)),
            'nutrition': request.form.get('nutrition', ''),
            'activity': request.form.get('activity', ''),
            'sleep': request.form.get('sleep', ''),
            'stress': request.form.get('stress', ''),
            'digital': request.form.get('digital', ''),
            'habits': request.form.get('habits', ''),
            'religion': request.form.get('religion', ''),
            'goals': request.form.get('goals', '')
        }
        
        session_id = session.get('session_id', str(uuid.uuid4()))
        
        # Check if report already exists
        report = HealthReport.query.filter_by(session_id=session_id).first()
        if not report:
            report = HealthReport(session_id=session_id)
            db.session.add(report)
        
        # Save user data
        report.set_user_data(user_data)
        
        # Generate free report
        free_report = generate_health_report(user_data, report_type='free')
        report.free_report = free_report
        
        db.session.commit()
        
        return redirect(url_for('show_report', session_id=session_id))
        
    except Exception as e:
        app.logger.error(f"Error processing questionnaire: {e}")
        flash('Произошла ошибка при обработке анкеты. Попробуйте снова.', 'error')
        return redirect(url_for('questionnaire'))

@app.route('/report/<session_id>')
def show_report(session_id):
    """Display health report"""
    report = HealthReport.query.filter_by(session_id=session_id).first()
    if not report:
        flash('Отчет не найден.', 'error')
        return redirect(url_for('index'))
    
    return render_template('report.html', report=report)

@app.route('/buy_full_report/<session_id>')
def buy_full_report(session_id):
    """Show Kaspi payment information for full report"""
    try:
        report = HealthReport.query.filter_by(session_id=session_id).first()
        if not report:
            flash('Отчет не найден.', 'error')
            return redirect(url_for('index'))
        
        # Generate unique payment ID
        payment_id = f"HEALTH_{session_id[:8]}_{uuid.uuid4().hex[:6].upper()}"
        report.payment_session_id = payment_id
        db.session.commit()
        
        return render_template('kaspi_payment.html', 
                             session_id=session_id, 
                             payment_id=payment_id,
                             amount=999)
        
    except Exception as e:
        app.logger.error(f"Error creating payment: {e}")
        flash('Ошибка при создании платежа. Попробуйте снова.', 'error')
        return redirect(url_for('show_report', session_id=session_id))

@app.route('/payment_success/<session_id>')
def payment_success(session_id):
    """Handle successful payment"""
    try:
        report = HealthReport.query.filter_by(session_id=session_id).first()
        if not report:
            flash('Отчет не найден.', 'error')
            return redirect(url_for('index'))
        
        # Generate full detailed report
        user_data = report.get_user_data()
        paid_report = generate_health_report(user_data, report_type='full')
        
        report.paid_report = paid_report
        report.is_paid = True
        db.session.commit()
        
        return render_template('payment_success.html', session_id=session_id)
        
    except Exception as e:
        app.logger.error(f"Error processing payment success: {e}")
        flash('Ошибка при обработке платежа.', 'error')
        return redirect(url_for('show_report', session_id=session_id))

@app.route('/payment_cancel/<session_id>')
def payment_cancel(session_id):
    """Handle cancelled payment"""
    return render_template('payment_cancel.html', session_id=session_id)

@app.route('/download_pdf/<session_id>')
def download_pdf(session_id):
    """Generate and download PDF report"""
    try:
        report = HealthReport.query.filter_by(session_id=session_id).first()
        if not report or not report.is_paid:
            flash('Доступ к PDF требует оплаты полной версии отчета.', 'error')
            return redirect(url_for('show_report', session_id=session_id))
        
        # Generate PDF
        user_data = report.get_user_data()
        pdf_path = generate_pdf_report(user_data, report.paid_report, session_id)
        
        return send_file(pdf_path, as_attachment=True, download_name=f'health_report_{session_id}.pdf')
        
    except Exception as e:
        app.logger.error(f"Error generating PDF: {e}")
        flash('Ошибка при генерации PDF.', 'error')
        return redirect(url_for('show_report', session_id=session_id))

@app.route('/confirm_payment/<session_id>', methods=['POST'])
def confirm_payment(session_id):
    """Manually confirm payment for Kaspi payments"""
    try:
        report = HealthReport.query.filter_by(session_id=session_id).first()
        if not report:
            flash('Отчет не найден.', 'error')
            return redirect(url_for('index'))
        
        # In a real implementation, you would verify the payment with Kaspi API
        # For now, we'll allow manual confirmation
        payment_confirmed = request.form.get('payment_confirmed') == 'true'
        
        if payment_confirmed:
            # Generate full detailed report
            user_data = report.get_user_data()
            paid_report = generate_health_report(user_data, report_type='full')
            
            report.paid_report = paid_report
            report.is_paid = True
            db.session.commit()
            
            return redirect(url_for('payment_success', session_id=session_id))
        else:
            flash('Платеж не подтвержден.', 'error')
            return redirect(url_for('show_report', session_id=session_id))
    
    except Exception as e:
        app.logger.error(f"Error confirming payment: {e}")
        flash('Ошибка при подтверждении платежа.', 'error')
        return redirect(url_for('show_report', session_id=session_id))
