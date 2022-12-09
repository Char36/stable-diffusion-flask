from typing import List

from app import imagine_service_pb2_grpc
from optimizedSD.arguments import Arguments
from optimizedSD.optimized_txt2img import StableDiffusionTxt2Img
from imagine_service_pb2_grpc import imagine__service__pb2
import logging
from concurrent import futures
import grpc

models_path = 'models/ldm/stable-diffusion-v1/'
model = StableDiffusionTxt2Img()

generating = False


def get_arguments(request: imagine__service__pb2.ImagineRequest) -> Arguments:
    # TODO: map request (this does not work)
    arguments = Arguments()
    arguments.__dict__ = request.__dict__.copy()
    return arguments


def build_response(result) -> imagine__service__pb2.ImagineResponse:
    imagine_response = imagine__service__pb2.ImagineResponse()
    imagine_response.image_data[:] = map_image_data(result)
    return imagine_response


def map_image_data(result) -> List[imagine__service__pb2.ImageData]:
    for image in result:
        image_data = imagine__service__pb2.ImageData()
        image_data.seed = image.seed
        image_data.chunk_data = image.data
        yield image_data


class StableDiffusion(imagine_service_pb2_grpc.StableDiffusionServiceServicer):

    def TextToImage(self,
                    request: imagine__service__pb2.ImagineRequest,
                    context) -> imagine__service__pb2.ImagineResponse:
        """
         Route for generating and returning `n` image results,
         where `n` :== `args.n_samples`

         Serialized as an array of B64-encoded byte arrays.
        """

        global generating
        global model

        if generating:
            raise Exception('text-to-image operation is already running')

        args = get_arguments(request)

        generating = True
        try:
            result = model.imagine(args, image_format='binary')
        finally:
            generating = False

        return build_response(result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    imagine_service_pb2_grpc.add_StableDiffusionServiceServicer_to_server(
        StableDiffusion(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('server started')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
