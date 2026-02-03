from unittest import mock

from kafka.errors import KafkaError

from coruscant.services.kafka import send_message


class TestKafka:
    @mock.patch("coruscant.services.kafka.get_producer")
    @mock.patch("coruscant.services.kafka.logger")
    def test_send_message__success(self, mock_logger, mock_get_producer):
        mock_producer = mock.Mock()
        mock_future = mock.Mock()
        mock_record_metadata = mock.Mock()
        mock_record_metadata.topic = "odin"
        mock_record_metadata.partition = 0
        mock_record_metadata.offset = 123
        mock_future.get.return_value = mock_record_metadata
        mock_producer.send.return_value = mock_future
        mock_get_producer.return_value = mock_producer

        result = send_message(topic="odin", message={"relay_id": "test", "state": "ON"}, key="test")

        assert result is True
        mock_producer.send.assert_called_once_with("odin", value={"relay_id": "test", "state": "ON"}, key="test")
        assert mock_logger.error.call_count == 0
        assert "Message sent to topic odin partition 0 offset 123" in mock_logger.info.call_args[0][0]

    @mock.patch("coruscant.services.kafka.get_producer")
    @mock.patch("coruscant.services.kafka.logger")
    def test_send_message__kafka_error(self, mock_logger, mock_get_producer):
        mock_producer = mock.Mock()
        mock_producer.send.side_effect = KafkaError("Connection failed")
        mock_get_producer.return_value = mock_producer

        result = send_message(topic="odin", message={"relay_id": "test", "state": "ON"})

        assert result is False
        mock_producer.send.assert_called_once()
        assert mock_logger.error.call_count == 1
        assert "Kafka error: KafkaError: Connection failed" in mock_logger.error.call_args[0][0]

    @mock.patch("coruscant.services.kafka.get_producer")
    @mock.patch("coruscant.services.kafka.logger")
    def test_send_message__unexpected_error(self, mock_logger, mock_get_producer):
        mock_producer = mock.Mock()
        mock_producer.send.side_effect = Exception("Unexpected error")
        mock_get_producer.return_value = mock_producer

        result = send_message(topic="odin", message={"relay_id": "test", "state": "ON"})

        assert result is False
        mock_producer.send.assert_called_once()
        assert mock_logger.error.call_count == 1
        assert "Unexpected error sending message: Unexpected error" in mock_logger.error.call_args[0][0]

    @mock.patch("coruscant.services.kafka.get_producer")
    @mock.patch("coruscant.services.kafka.logger")
    def test_send_message__without_key(self, mock_logger, mock_get_producer):
        mock_producer = mock.Mock()
        mock_future = mock.Mock()
        mock_record_metadata = mock.Mock()
        mock_record_metadata.topic = "odin"
        mock_record_metadata.partition = 1
        mock_record_metadata.offset = 456
        mock_future.get.return_value = mock_record_metadata
        mock_producer.send.return_value = mock_future
        mock_get_producer.return_value = mock_producer

        result = send_message(topic="odin", message={"relay_id": "test", "state": "ON"})

        assert result is True
        mock_producer.send.assert_called_once_with("odin", value={"relay_id": "test", "state": "ON"}, key=None)
