from django.core.management.base import BaseCommand
from django.db.models import F

from ledger.payments.models import OracleInterfaceSystem, PaymentTotal, OracleInterfaceReportReceipient

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))
        
        systems = OracleInterfaceSystem.objects.filter(enabled=True)

        for system in systems:
            with_discrepancies = PaymentTotal.objects.filter(
                oracle_system=system,
            ).exclude(
                bpoint_gateway_total=F('oracle_receipt_total')
            ).order_by('-settlement_date')

            #format

            #send email

            recipients = list(OracleInterfaceReportReceipient.objects.filter(system=system).values_list('email', flat=True))
