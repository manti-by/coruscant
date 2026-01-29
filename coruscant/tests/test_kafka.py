from unittest import mock

from kafka.errors import KafkaError

from coruscant.services.kafka import close_producer, get_producer, send_message


class TestKafka:
    @mock.patch("coruscant.services.kafka.KafkaProducer")
    @mock.patch("coruscant.services.kafka.logger")
    def test_get_producer__creates_new_producer(self, mock_logger, mock_kafka_producer):
        close_producer()

        producer = get_producer()

        assert producer == mock_kafka_producer.return_value
        mock_kafka_producer.assert_called_once_with(
            bootstrap_servers=["192.168.1.100:9092"],
            value_serializer=mock.ANY,
            key_serializer=mock.ANY,
        )
        assert mock_logger.error.call_count == 0

    @mock.patch("coruscant.services.kafka.KafkaProducer")
    @mock.patch("coruscant.services.kafka.logger")
    def test_get_producer__returns_existing_producer(self, mock_logger, mock_kafka_producer):
        close_producer()

        producer1 = get_producer()
        producer2 = get_producer()

        assert producer1 is producer2
        mock_kafka_producer.assert_called_once()

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

    @mock.patch("coruscant.services.kafka.KafkaProducer")
    def test_close_producer(self, mock_kafka_producer):
        close_producer()
        producer = get_producer()

        close_producer()

        producer.close.assert_called_once()
