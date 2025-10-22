from flask_mail import Message
from flask import current_app
import os


class EmailService:
    @staticmethod
    def send_key_shard(recipient_email: str, shard_data: dict, user_email: str):
        """Отправляет shard ключа участнику команды"""

        shard_info = f"""
        Shard ID: {shard_data['shard_id']}
        Total Shards: {shard_data['total_shards']}
        Required for access: {shard_data['threshold']}
        """

        msg = Message(
            subject=f'🔐 Key Shard for {user_email} - Multi-Signature Access',
            recipients=[recipient_email],
            body=f'''
            Hello!

            You have been added as a team member for the multi-signature wallet {user_email}.

            Your key shard information:
            {shard_info}

            Keep this information secure! You will need it along with other team members to access the wallet.

            Security reminder: Never share your shard with anyone.
            ''',
            html=f'''
            <h2>🔐 Multi-Signature Key Shard</h2>
            <p>You have been added as a team member for <strong>{user_email}</strong></p>

            <h3>Your Key Shard Information:</h3>
            <ul>
                <li><strong>Shard ID:</strong> {shard_data['shard_id']}</li>
                <li><strong>Total Shards:</strong> {shard_data['total_shards']}</li>
                <li><strong>Required for access:</strong> {shard_data['threshold']}</li>
            </ul>

            <p><strong>⚠️ Security Reminder:</strong> Never share your shard with anyone.</p>
            '''
        )

        # Для разработки - просто выводим в консоль
        if os.environ.get('FLASK_ENV') == 'development':
            print(f"📧 EMAIL TO: {recipient_email}")
            print(f"📦 SHARD DATA: {shard_data}")
        else:
            current_app.extensions['mail'].send(msg)