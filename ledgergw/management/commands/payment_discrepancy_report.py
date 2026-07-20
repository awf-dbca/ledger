from django.core.management.base import BaseCommand
from django.db.models import F

from ledger.payments.emails import send_discrepency_report
from ledger.payments.models import OracleInterfaceSystem, PaymentTotal, OracleInterfaceReportReceipient

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))
        
        systems = OracleInterfaceSystem.objects.filter(enabled=True)

        for system in systems:
            try:

                #TODO date filter?
                discrepancies = PaymentTotal.objects.filter(
                    oracle_system=system,
                ).exclude(
                    bpoint_gateway_total=F('oracle_receipt_total')
                ).order_by('-settlement_date')

                #format
                discrepancies_formatted = []
                for discrepancy in discrepancies:
                    row = {}
                    row['id'] = discrepancy.id
                    row['oracle_system_id'] = discrepancy.oracle_system_id
                    row['oracle_system_id_code'] = discrepancy.oracle_system.system_id
                    row['settlement_date'] = discrepancy.settlement_date.strftime('%d %b %Y')  
                    row['bpoint_gateway_total'] = str(discrepancy.bpoint_gateway_total)
                    row['ledger_bpoint_total'] = str(discrepancy.ledger_bpoint_total)
                    row['oracle_parser_total'] = str(discrepancy.oracle_parser_total)
                    row['oracle_receipt_total'] = str(discrepancy.oracle_receipt_total)
                    row['cash_total'] = str(discrepancy.cash_total)
                    row['bpay_total'] = str(discrepancy.bpay_total)
                    discrepancy_status = False
                    if discrepancy.bpoint_gateway_total != discrepancy.oracle_receipt_total:
                        discrepancy_status = True
                    row['discrepancy'] = discrepancy_status
                    row['updated'] = discrepancy.updated.strftime('%d/%m/%Y %H:%M:%S')

                    discrepancies_formatted.append(row)

                #send email
                recipients = list(OracleInterfaceReportReceipient.objects.filter(system=system).values_list('email', flat=True))
                send_discrepency_report(system, discrepancies_formatted, recipients)

            except Exception as e:
                logger.error("Failed to send discrepancy report with error:", e)
